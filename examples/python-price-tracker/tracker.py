"""Track a small product basket with the datawebot MCP server and keep a dated
history in SQLite. Run it on a schedule (cron, GitHub Actions); each run adds
one row per seller offer and prints what changed since the previous run."""
import itertools, json, os, re, sqlite3, time, urllib.request
from datetime import datetime, timezone

MCP_URL = "https://mcp.datawebot.com/mcp"
DB_PATH = os.environ.get("TRACKER_DB", "prices.db")

# What to track. "must" words have to appear in the listing title, "reject"
# words must not, and anything below min_price is treated as a different item
# (an accessory, a rental fee or a bait listing).
WATCHLIST = [
    {"item": "switch2", "query": "Nintendo Switch 2 console", "must": ["switch 2"],
     "reject": ["refurbished", "pre-owned", "used", "rent", "bundle", "+", "accessories", "mario", "pokemon"],
     "min_price": 400},
    {"item": "dyson-v15", "query": "Dyson V15 Detect", "must": ["v15 detect"],
     "reject": ["refurbished", "absolute", "extra", "total clean", "submarine", " pro", "v15s"],
     "min_price": 300},
    {"item": "ninja-af101", "query": "Ninja AF101 air fryer", "must": ["af101"],
     "reject": ["refurbished", "pre-owned", "used", "basket only", "replacement"],
     "min_price": 50},
]


def api_key():
    key = os.environ.get("DATAWEBOT_API_KEY")
    if key:
        return key
    # Written by the agent setup (https://mcp.datawebot.com/setup.md).
    with open(os.path.expanduser("~/.datawebot/credentials")) as f:
        return json.load(f)["profiles"]["https://mcp.datawebot.com"]["api_key"]


def call_tool(name, arguments):
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": name, "arguments": arguments}}
    req = urllib.request.Request(MCP_URL, data=json.dumps(body).encode(), headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": "Bearer " + api_key()})
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read().decode()
    if raw.startswith("event:") or "\ndata:" in raw:  # streamed reply
        raw = "\n".join(l[5:].strip() for l in raw.splitlines() if l.startswith("data:"))
    reply = json.loads(raw)
    if "error" in reply:
        raise RuntimeError(f"{name} failed: {reply['error'].get('message')}")
    result = reply["result"]
    payload = result.get("structuredContent") or json.loads(result["content"][0]["text"])
    if result.get("isError"):
        raise RuntimeError(f"{name} failed: {json.dumps(payload)[:300]}")
    return payload


def ask(name, arguments):
    """Call a tool; when it answers "working", collect the answer with get_results."""
    res = call_tool(name, arguments)
    for _ in range(12):
        if res["data"].get("status") != "working":
            return res
        time.sleep(res["data"].get("check_after_seconds") or 5)
        res = call_tool("get_results", {"request_id": res["data"]["request_id"]})
    raise RuntimeError(f"{name} was still working after a minute; the next run tries again")


def amount(listing):
    return (listing.get("price") or {}).get("amount")


def matches(title, spec):
    t = " " + (title or "").lower() + " "
    return all(w in t for w in spec["must"]) and not any(w in t for w in spec["reject"])


def candidates(spec):
    found = ask("search_products", {"query": spec["query"], "country": "US", "limit": 10})
    for p in found["data"]["products"]:  # organic results; ads come back separately
        if p.get("product_id") and (amount(p) or 0) >= spec["min_price"] and matches(p["title"], spec):
            yield p


def setup(db):
    db.execute("""CREATE TABLE IF NOT EXISTS observations (
        checked_at TEXT, as_of TEXT, item TEXT, product_id TEXT, shop TEXT,
        title TEXT, price REAL, total REAL, currency TEXT, url TEXT)""")


def total_of(offer):
    m = re.search(r"[\d,]+\.?\d*", offer.get("total_text") or "")
    return float(m.group().replace(",", "")) if m else amount(offer)


def run():
    db = sqlite3.connect(DB_PATH)
    setup(db)
    checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for spec in WATCHLIST:
        product = res = None
        try:
            # A result sold by one shop has no seller list; read at most two matches.
            for p in itertools.islice(candidates(spec), 2):
                res = ask("get_product", {"product_id": p["product_id"]})
                if res["data"].get("offers"):
                    product = p
                    break
        except Exception as e:  # a failed call is a gap in the history, not a zero
            print(f"{spec['item']}: {e}")
            continue
        if not product:
            print(f"{spec['item']}: no clean match with a seller list in this search; nothing stored")
            continue
        as_of, offers = res["meta"]["as_of"], res["data"]["offers"]
        kept = [o for o in offers if o.get("url") and (amount(o) or 0) >= spec["min_price"]
                and matches(o.get("title"), spec)]
        prev = dict(db.execute("""SELECT url, total FROM observations WHERE item = ? AND checked_at =
            (SELECT MAX(checked_at) FROM observations WHERE item = ? AND checked_at < ?)""",
            (spec["item"], spec["item"], checked_at)).fetchall())
        for o in kept:
            total, url = total_of(o), o["url"].split("?")[0]  # drop tracking parameters
            shop, currency = o.get("shop") or "?", o["price"].get("currency") or ""
            db.execute("INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?,?)",
                       (checked_at, as_of, spec["item"], product["product_id"], shop,
                        o["title"], amount(o), total, currency, url))
            old = prev.get(url)
            note = "new listing" if old is None else ("unchanged" if old == total else f"was {old:.2f}")
            print(f"{spec['item']:12} {shop[:26]:26} {total:8.2f} {currency} {note}")
        print(f"{spec['item']}: kept {len(kept)} offers, dropped {len(offers) - len(kept)}, as_of {as_of}")
    db.commit()


if __name__ == "__main__":
    run()
