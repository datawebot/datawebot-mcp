# Python price tracker

Tracks a small basket of products with the datawebot MCP server and keeps a dated history in SQLite. Each run adds one row per seller offer and prints what changed since the previous run. Standard library only.

## Run

```bash
export DATAWEBOT_API_KEY="..."   # from https://www.datawebot.com/dashboard → API keys
python3 tracker.py
```

If `DATAWEBOT_API_KEY` is not set, the script reads the key saved by the agent setup (`~/.datawebot/credentials`).

Edit the basket and the matching rules at the top of `tracker.py`. Run it on a schedule (cron, GitHub Actions) to build a history. Each run makes one search and one product read per item, paid in credits (new accounts start with 200 free). Every answer reports `credits_used` and `credits_left` in `meta`, so size the basket to your balance.

The full walkthrough, including real output from 18 Oct 2026 and the matching rules, is at [datawebot.com/blog/price-tracker-python](https://www.datawebot.com/blog/price-tracker-python).
