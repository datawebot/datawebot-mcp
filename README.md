# datawebot MCP server

Ask your agent who sells it and for how much. datawebot finds a product in online shops around the world and returns every seller's price with a direct link, in seconds.

- **Server URL:** `https://mcp.datawebot.com/mcp` (remote, streamable HTTP)
- **Sign-in:** free, by email approval. No password, no card.
- **Website:** [datawebot.com](https://www.datawebot.com) · [Docs for agents](https://www.datawebot.com/docs/agents)

This repository holds the public connection details, the MCP Registry entry (`server.json`) and working examples. The server itself is hosted; there is nothing to install.

## What it can do today

| Tool | What it returns |
| --- | --- |
| `search_products` | Products for sale across online shops worldwide, in local languages: title, price, original price, shop, rating, review count, image, condition, link and retrieval time. Filter by country and, optionally, by shop domains. |
| `get_product_offers` | For one product from a search: each seller's price, total with shipping, delivery note, seller rating and a direct link to the product page. |
| `discover` | Lists every tool available now, including ones added after your session started. Call it first. |
| `list_job_blueprints`, `submit_job`, `get_job`, `get_results` | Amazon search-result and product-page extraction Jobs. In preview and opening to all accounts soon. |

Results are best-effort snapshots with the time they were retrieved. They are not verified or guaranteed-current prices. datawebot does not store price history, run scheduled checks or send alerts; your agent or script keeps whatever it needs. Shopify store extraction is temporarily unavailable and coming back.

There is a free daily allowance per account. Each response reports what is left.

## Connect

### Claude (claude.ai and Claude desktop)

Settings → Connectors → **Add custom connector** → URL `https://mcp.datawebot.com/mcp` → Connect, then approve the email from datawebot.

### ChatGPT

Add a custom MCP server with the URL `https://mcp.datawebot.com/mcp` and OAuth authentication (needs a plan and workspace that allow custom MCP servers).

### Claude Code

```bash
claude mcp add --transport http datawebot https://mcp.datawebot.com/mcp
```

Or tell any coding agent with a shell: `set up https://mcp.datawebot.com/setup.md`. It reads the file, asks for your email and saves the key itself, so no key is pasted into a chat.

### Cursor

`~/.cursor/mcp.json` or `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "datawebot": { "url": "https://mcp.datawebot.com/mcp" }
  }
}
```

### VS Code

`.vscode/mcp.json`:

```json
{
  "servers": {
    "datawebot": { "type": "http", "url": "https://mcp.datawebot.com/mcp" }
  }
}
```

### Scripts, n8n and agent frameworks (API key)

Tools that can't do the email sign-in use an API key. Sign in at [datawebot.com/dashboard](https://www.datawebot.com/dashboard) → **API keys**, create a key (30 days, 90 days or 1 year) and send it as a header:

```
Authorization: Bearer <your API key>
```

Any client that can call a remote MCP server with a header works, for example n8n's MCP Client tool, LangChain's `langchain-mcp-adapters`, the OpenAI Agents SDK, the Vercel AI SDK and CrewAI. Keep the key in an environment variable or your tool's credential store, never in code.

## Examples

- [`examples/python-price-tracker`](examples/python-price-tracker): a basket price tracker in plain Python (standard library only) that stores dated rows in SQLite and reports changes. It was run against the live server on 18 Oct 2026; the walkthrough is in [Build a price tracker with an AI agent](https://www.datawebot.com/blog/price-tracker-python).

## Support

Email [hello@datawebot.com](mailto:hello@datawebot.com) or open an issue in this repository.

## Privacy

See the [privacy policy](https://www.datawebot.com/privacy).

## License

The examples and documentation in this repository are MIT licensed. Use of the hosted service is covered by the [terms](https://www.datawebot.com/terms).
