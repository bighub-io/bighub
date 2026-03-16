# @bighub/bighub-mcp

> MCP server for decision learning on agent actions.

Use BIGHUB from any [Model Context Protocol](https://modelcontextprotocol.io) client to evaluate agent actions, report real outcomes, retrieve similar past cases, and improve future decisions over time.

```text
MCP client
   ↓
@bighub/bighub-mcp
   ↓
BIGHUB API
   ↓
evaluate -> execute -> report outcome -> learn
```

---

## Install

```bash
npm install @bighub/bighub-mcp
```

Requires Node.js 18+.

---

## Quickstart

Set your API key:

```bash
export BIGHUB_API_KEY=your_api_key
```

Run the server in stdio mode:

```bash
npx @bighub/bighub-mcp
```

Add it to your MCP client configuration:

```json
{
  "mcpServers": {
    "bighub": {
      "command": "npx",
      "args": ["@bighub/bighub-mcp"],
      "env": {
        "BIGHUB_API_KEY": "your_api_key"
      }
    }
  }
}
```

Works with MCP-compatible clients such as Claude Desktop and Cursor.

---

## Core MCP Tools

Most teams start with the first three tools (the core loop):

| Tool | Purpose |
|---|---|
| `bighub_actions_submit` | Submit an action for evaluation before execution |
| `bighub_outcomes_report` | Report what actually happened |
| `bighub_precedents_query` | Retrieve similar past cases |
| `bighub_calibration_report` | Compare prediction vs reality |
| `bighub_insights_advise` | Retrieve learned guidance for the next action |

`bighub_actions_submit_v2` is available as an advanced action submission endpoint.

---

## Typical MCP Loop

1. Evaluate the action
2. Execute it in your runtime
3. Report the real outcome
4. Retrieve similar past cases
5. Compare prediction vs reality
6. Use learned guidance on the next action

Typical tool flow:

```text
bighub_actions_submit
-> agent runtime executes action
-> bighub_outcomes_report
-> bighub_precedents_query
-> bighub_calibration_report
-> bighub_insights_advise
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `BIGHUB_API_KEY` | Yes* | - | API key auth |
| `BIGHUB_BEARER_TOKEN` | No | - | Alternative bearer auth |
| `BIGHUB_BASE_URL` | No | `https://api.bighub.io` | API base URL |
| `BIGHUB_TIMEOUT_MS` | No | `15000` | Request timeout |
| `BIGHUB_MAX_RETRIES` | No | `2` | Retries on transient failures |
| `BIGHUB_ALLOW_INSECURE_HTTP` | No | - | Allow HTTP for local/private testing |

\* One of `BIGHUB_API_KEY` or `BIGHUB_BEARER_TOKEN` is required.

Some management tools (for example API key and webhook administration) require user JWT auth and should be used with `BIGHUB_BEARER_TOKEN`.

---

## Free BETA

Current Free BETA limits:

- 3 agents
- 2,500 actions / month
- 30 days history
- 1 environment

---

## Local Development

```bash
git clone https://github.com/bighub-io/bighub.git
cd bighub/servers/mcp
npm install
npm run test
npm run check
npm run build
npm run start
npm run dev
```

---

## Links

- [bighub.io](https://bighub.io)
- [GitHub - bighub-io/bighub](https://github.com/bighub-io/bighub)
- [npm - @bighub/bighub-mcp](https://www.npmjs.com/package/@bighub/bighub-mcp)
- [PyPI - bighub (Python SDK)](https://pypi.org/project/bighub/)
- [PyPI - bighub-openai](https://pypi.org/project/bighub-openai/)

---

## License

MIT
