# Installing the datawebot MCP server (for Cline and other agents)

datawebot is a hosted remote MCP server. There is nothing to clone, build or install: you only add one entry to the MCP settings and the user signs in.

- Server URL: `https://mcp.datawebot.com/mcp`
- Transport: Streamable HTTP
- Auth: OAuth 2.0 (free email sign-in, no password, no card). An API key header is the fallback for clients that cannot do OAuth.

## Step 1: add the server

Add this entry under `mcpServers` in Cline's MCP settings file (`cline_mcp_settings.json`; in the extension open **MCP Servers → Configure → Configure MCP Servers**, in Cline CLI it is `~/.cline/data/settings/cline_mcp_settings.json`). Keep any servers that are already there.

```json
{
  "mcpServers": {
    "datawebot": {
      "type": "streamableHttp",
      "url": "https://mcp.datawebot.com/mcp",
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Set `"type": "streamableHttp"` explicitly. Without it Cline falls back to the legacy SSE transport, which this server does not use.

Alternatives that give the same result:

- In the extension, **MCP Servers → Remote Servers**: Server Name `datawebot`, Server URL `https://mcp.datawebot.com/mcp`, Transport Type **Streamable HTTP**, then **Add Server**.
- In Cline CLI: `cline mcp add datawebot https://mcp.datawebot.com/mcp --transport http --yes`

## Step 2: sign in

The server answers unauthenticated requests with `401` and a `WWW-Authenticate` header that points to its OAuth metadata, so Cline marks it as needing authorization.

1. Ask the user to open **MCP Servers** in Cline and click **Authenticate** on the `datawebot` row (in Cline CLI, run `cline mcp` and choose **Authorize OAuth**).
2. A browser page opens. The user enters their email address and approves the sign-in email from datawebot.
3. Back in Cline the server turns green and its tools load.

Do not ask the user to paste passwords or keys into the chat for this step. OAuth needs no key.

## Fallback: API key (only if OAuth sign-in is not possible)

1. The user signs in at https://www.datawebot.com/dashboard, opens **API keys** and creates a key.
2. The user adds it to the same settings entry as a header (they can paste it into the settings file themselves):

```json
{
  "mcpServers": {
    "datawebot": {
      "type": "streamableHttp",
      "url": "https://mcp.datawebot.com/mcp",
      "headers": {
        "Authorization": "Bearer <API key>"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Step 3: check it works

1. Call `discover`. It lists every tool available to this account right now.
2. Call `search_products` with a simple query, for example `{"query": "Sony WH-1000XM5", "country": "US"}`, and show the user a few results with title, price, shop and link.
3. For one result, call `get_product` with its `product_id` to list each seller's price, total with shipping and a direct link.

Results are best-effort snapshots and carry the time they were retrieved. Do not present prices as verified or current. Searches and product reads cost credits (200 free credits per account); failed or empty ones are free. Call `get_account` for the credits left.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| Server stays red with a 401 / unauthorized error | Click **Authenticate** (or `cline mcp` → **Authorize OAuth**) and approve the sign-in email. |
| Connection fails right after adding | Check that `"type"` is `"streamableHttp"` and the URL ends in `/mcp`. |
| A tool you expected is missing | Call `discover`; it returns the tools open to this account. |

Docs: https://www.datawebot.com/docs/agents · Support: hello@datawebot.com
