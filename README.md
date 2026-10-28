# datawebot MCP server

[![Add to Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/install-mcp?name=datawebot&config=eyJ1cmwiOiJodHRwczovL21jcC5kYXRhd2Vib3QuY29tL21jcCJ9)
[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_datawebot-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://vscode.dev/redirect/mcp/install?name=datawebot&config=%7B%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fmcp.datawebot.com%2Fmcp%22%7D)
[![Add to LM Studio](https://files.lmstudio.ai/deeplink/mcp-install-dark.svg)](https://lmstudio.ai/install-mcp?name=datawebot&config=eyJ1cmwiOiJodHRwczovL21jcC5kYXRhd2Vib3QuY29tL21jcCJ9)

Ask your agent who sells it and for how much. datawebot finds a product in online shops around the world and returns every seller's price with a direct link, in seconds.

- **Server URL:** `https://mcp.datawebot.com/mcp` (remote, streamable HTTP)
- **Sign-in:** free, by email approval. No password, no card. OAuth 2.1 per the MCP authorization spec, or an API key (see [Authentication](#authentication)).
- **Website:** [datawebot.com](https://www.datawebot.com) · [Docs for agents](https://www.datawebot.com/docs/agents)

This repository holds the public connection details, the MCP Registry entry (`server.json`), the Cursor plugin manifest (`.cursor-plugin/plugin.json`, `mcp.json`), the Claude Code plugin (`.claude-plugin/`, `.mcp.json`), the Gemini CLI extension (`gemini-extension.json`, `GEMINI.md`), an agent skill (`skills/datawebot/SKILL.md`), agent install notes (`llms-install.md`) and working examples. The server itself is hosted; there is nothing to install.

## What it can do today

| Tool | What it returns |
| --- | --- |
| `discover` | Lists every tool available now, including ones added after your session started. Call it first. |
| `search_products` | Products for sale across online stores around the world, from Amazon and Walmart to brand stores, in local languages: title, price, original price, shop, rating, review count, image, condition, link and retrieval time. Filter by country and, optionally, by shop. |
| `get_product` | One product's details by URL or `product_id`. For a product sold by several shops: each seller's price, total with shipping, delivery note, seller rating and a direct link to the product page. |
| `get_results` | Collects an answer that was still working when first asked. |
| `find_endpoints`, `submit_job` | Extraction Jobs on a store's exact endpoints: search, catalogue, category and product pages. `find_endpoints` is free and lists what a store supports, with prices and page limits; `submit_job` runs one on one URL. |
| `check_site`, `get_account` | Price a store before you spend, and see the credits left. |

Searches, product reads and Jobs are paid in credits. New accounts start with 200 free credits, and more can be bought on the [dashboard](https://www.datawebot.com/dashboard). Failed or empty requests are free.

Results are best-effort snapshots with the time they were retrieved. They are not verified or guaranteed-current prices. datawebot does not store price history, run scheduled checks or send alerts; your agent or script keeps whatever it needs.

Call `get_account` for the credits left.

## Connect

### Claude (claude.ai and Claude desktop)

Settings → Connectors → **Add custom connector** → URL `https://mcp.datawebot.com/mcp` → Connect, then approve the email from datawebot.

### ChatGPT

Add a custom MCP server with the URL `https://mcp.datawebot.com/mcp` and OAuth authentication (needs a plan and workspace that allow custom MCP servers).

### Claude Code

Install the datawebot plugin, which adds the MCP server and the datawebot skill. In a Claude Code session:

```text
/plugin install datawebot --marketplace datawebot/datawebot-mcp
```

On Claude Code versions before 2.1.275, add the marketplace first, then install:

```text
/plugin marketplace add datawebot/datawebot-mcp
/plugin install datawebot@datawebot
```

Then run `/mcp`, choose `datawebot` and approve the sign-in email. To add only the MCP server, without the plugin:

```bash
claude mcp add --transport http datawebot https://mcp.datawebot.com/mcp
```

Or tell any coding agent with a shell: `set up https://mcp.datawebot.com/setup.md`. It reads the file, asks for your email and saves the key itself, so no key is pasted into a chat.

### Gemini CLI

```bash
gemini extensions install https://github.com/datawebot/datawebot-mcp
```

The extension adds the MCP server, a short `GEMINI.md` context file and the datawebot skill. Start `gemini`; the server asks for sign-in on first use, or run `/mcp auth datawebot` and approve the email from datawebot.

### Cursor

Click **Add to Cursor** at the top of this page, or paste this link into your browser:

```
cursor://anysphere.cursor-deeplink/mcp/install?name=datawebot&config=eyJ1cmwiOiJodHRwczovL21jcC5kYXRhd2Vib3QuY29tL21jcCJ9
```

This repository is also a Cursor plugin (`.cursor-plugin/plugin.json` and `mcp.json`). Or add it by hand to `~/.cursor/mcp.json` or `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "datawebot": { "url": "https://mcp.datawebot.com/mcp" }
  }
}
```

### VS Code

Click **Install in VS Code** at the top of this page, or add it to `.vscode/mcp.json`:

```json
{
  "servers": {
    "datawebot": { "type": "http", "url": "https://mcp.datawebot.com/mcp" }
  }
}
```

### Cline

**MCP Servers → Remote Servers**: Server Name `datawebot`, Server URL `https://mcp.datawebot.com/mcp`, Transport Type **Streamable HTTP** → **Add Server**, then click **Authenticate** on the server and approve the email from datawebot. To edit the settings file instead, use `"type": "streamableHttp"` (without it Cline uses legacy SSE):

```json
{
  "mcpServers": {
    "datawebot": { "type": "streamableHttp", "url": "https://mcp.datawebot.com/mcp" }
  }
}
```

Agents that install servers for you (such as Cline) can follow [`llms-install.md`](llms-install.md).

### LM Studio

Click **Add to LM Studio** at the top of this page (LM Studio 0.3.17 or later), or open this link:

```
lmstudio://add_mcp?name=datawebot&config=eyJ1cmwiOiJodHRwczovL21jcC5kYXRhd2Vib3QuY29tL21jcCJ9
```

It adds `{"url": "https://mcp.datawebot.com/mcp"}` to LM Studio's `mcp.json`.

### Replit

[Add to Replit](https://replit.com/integrations?mcp=eyJkaXNwbGF5TmFtZSI6ImRhdGF3ZWJvdCIsImJhc2VVcmwiOiJodHRwczovL21jcC5kYXRhd2Vib3QuY29tL21jcCJ9), then **Test & save** and approve the sign-in email from datawebot.

### Agent skill

[`skills/datawebot/SKILL.md`](skills/datawebot/SKILL.md) follows the [Agent Skills](https://agentskills.io) format. It teaches an agent the datawebot workflow: search, seller offers, extraction Jobs, credits and errors. The Claude Code plugin and the Gemini CLI extension include it; for other agents that read skills, copy the `skills/datawebot` folder into their skills directory.

### Scripts, n8n and agent frameworks (API key)

Tools that can't do the email sign-in use an API key. Sign in at [datawebot.com/dashboard](https://www.datawebot.com/dashboard) → **API keys**, create a key (30 days, 90 days or 1 year) and send it as a header:

```
Authorization: Bearer <your API key>
```

Any client that can call a remote MCP server with a header works, for example n8n's MCP Client tool, LangChain's `langchain-mcp-adapters`, the OpenAI Agents SDK, the Vercel AI SDK and CrewAI. Keep the key in an environment variable or your tool's credential store, never in code.

## Authentication

The server follows the MCP authorization spec. An unauthenticated request gets `401` with a `WWW-Authenticate` header pointing to the protected-resource metadata at `https://mcp.datawebot.com/.well-known/oauth-protected-resource/mcp`.

- **OAuth 2.1** (MCP clients such as Claude, ChatGPT, Cursor, VS Code, Cline, Gemini CLI): authorization code flow with PKCE (`S256`), dynamic client registration and refresh tokens. Authorization server metadata: `https://mcp.datawebot.com/.well-known/oauth-authorization-server`. Sign-in is by email approval.
- **API key** (scripts, n8n, agent frameworks): send `Authorization: Bearer <your API key>`; see the API key section above.

## Examples

- [`examples/python-price-tracker`](examples/python-price-tracker): a basket price tracker in plain Python (standard library only) that stores dated rows in SQLite and reports changes. It was run against the live server on 18 Oct 2026; the walkthrough is in [Build a price tracker with an AI agent](https://www.datawebot.com/blog/price-tracker-python).

## Support

Email [hello@datawebot.com](mailto:hello@datawebot.com) or open an issue in this repository.

## Privacy

See the [privacy policy](https://www.datawebot.com/privacy).

## License

The examples and documentation in this repository are MIT licensed. Use of the hosted service is covered by the [terms](https://www.datawebot.com/terms).
