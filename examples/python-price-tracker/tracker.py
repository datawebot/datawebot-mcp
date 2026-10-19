"""Track a small product basket with the datawebot MCP server and keep a dated
history in SQLite. Run it on a schedule (cron, GitHub Actions); each run adds
one row per seller offer and prints what changed since the previous run."""
import json, os, re, sqlite3, urllib.request
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
    result = json.loads(raw)["result"]
    payload = result.get("structuredContent") or json.loads(result["content"][0]["text"])
    if result.get("isError"):
        raise RuntimeError(f"{name} failed: {json.dumps(payload)[:300]}")
    return payload


def matches(title, spec):
    t = " " + title.lower() + " "
    return all(w in t for w in spec["must"]) and not any(w in t for w in spec["reject"])


def pick_product(spec):
    found = call_tool("search_products", {"query": spec["query"], "country": "US", "limit": 10})
    for r in found["data"]["results"]:
        if (r.get("product_id") and r.get("has_offers") and r.get("condition") in (None, "new")
                and r.get("price") and r["price"] >= spec["min_price"] and matches(r["title"], spec)):
            return r
    return None


def setup(db):
    db.execute("""CREATE TABLE IF NOT EXISTS observations (
        checked_at TEXT, as_of TEXT, item TEXT, product_id TEXT, shop TEXT,
        title TEXT, price REAL, total REAL, currency TEXT, url TEXT)""")


def total_of(offer):
    m = re.search(r"[\d,]+\.?\d*", offer.get("total_text") or "")
    return float(m.group().replace(",", "")) if m else offer.get("price")


def run():
    db = sqlite3.connect(DB_PATH)
    setup(db)
    checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for spec in WATCHLIST:
        try:
            product = pick_product(spec)
            if not product:
                print(f"{spec['item']}: no clean match in this search; nothing stored")
                continue
            res = call_tool("get_product_offers", {"product_id": product["product_id"],
                                                   "query": spec["query"], "country": "US"})
        except Exception as e:  # a failed call is a gap in the history, not a zero
            print(f"{spec['item']}: {e}")
            continue
        as_of = res["meta"]["as_of"]
        kept = [o for o in res["data"]["offers"]
                if o.get("price") and o["price"] >= spec["min_price"] and matches(o["title"], spec)]
        dropped = len(res["data"]["offers"]) - len(kept)
        prev = dict(db.execute("""SELECT url, total FROM observations WHERE item = ? AND checked_at =
            (SELECT MAX(checked_at) FROM observations WHERE item = ? AND checked_at < ?)""",
            (spec["item"], spec["item"], checked_at)).fetchall())
        for o in kept:
            total, url = total_of(o), o["url"].split("?")[0]  # drop tracking parameters
            db.execute("INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?,?)",
                       (checked_at, as_of, spec["item"], product["product_id"], o["shop"],
                        o["title"], o["price"], total, o["currency"], url))
            old = prev.get(url)
            note = "new listing" if old is None else ("unchanged" if old == total else f"was {old:.2f}")
            print(f"{spec['item']:12} {o['shop'][:26]:26} {total:8.2f} {o['currency']} {note}")
        print(f"{spec['item']}: kept {len(kept)} offers, dropped {dropped}, as_of {as_of}")
    db.commit()


if __name__ == "__main__":
    run()
