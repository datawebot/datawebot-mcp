# datawebot

The `datawebot` MCP server (https://mcp.datawebot.com/mcp) finds products for sale across online shops and lists each seller's price with a direct link. It also runs paid extraction Jobs for Amazon and supported stores.

- Call `discover` first; it lists the tools open to this account.
- If the tools return `login_required`, ask the user to run `/mcp auth datawebot` and approve the sign-in email. Never ask for a key in chat.
- Results are dated, best-effort snapshots: say when they were retrieved and never present a price as verified or current.
- For the full workflow, Jobs, credits and errors, use the `datawebot` skill (`skills/datawebot/SKILL.md`).
