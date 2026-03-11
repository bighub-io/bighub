# @bighub/bighub-mcp

> MCP server for decision intelligence and self-improving rules with BIGHUB.

Use BIGHUB from any [Model Context Protocol](https://modelcontextprotocol.io) client. This server exposes MCP tools that simulate, score, enforce, and learn from AI agent execution by calling the BIGHUB API — actions, rules, approvals, kill switch, events, API keys, webhooks, auth, and Future Memory.

```text
MCP Client (Claude, Cursor, etc.)
        ↓
@bighub/bighub-mcp  (stdio)
        ↓
BIGHUB Decision Intelligence API (api.bighub.io)
        ↓
simulate → score → execute / block / approve
```

---

## Install

```bash
npm install @bighub/bighub-mcp
```

Requires Node.js 18+.

---

## Quickstart

1. Set your API key:

```bash
export BIGHUB_API_KEY=your_api_key
```

2. Run the server in stdio mode:

```bash
npx @bighub/bighub-mcp
```

The server exposes MCP tools over stdio. Connect it to any MCP-compatible client (Claude Desktop, Cursor, etc.) by adding it to your MCP configuration:

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

---

## What BIGHUB does

BIGHUB simulates every agent action, learns from every decision, and makes your rules smarter over time. Every action is stress-tested across 100+ scenarios and scored for risk, fragility, and blast radius — before execution.

| Guardrails | BIGHUB |
|---|---|
| Block or allow | Simulate, score, enforce, and learn |
| Static rules | Rules that improve from every decision |
| No visibility into risk | Fragility, blast radius, and impact scored before execution |
| Same policy forever | Future Memory detects patterns and recommends smarter policies |

---

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BIGHUB_API_KEY` | Yes* | — | API key authentication (`X-API-Key` header) |
| `BIGHUB_BEARER_TOKEN` | No | — | Alternative auth (`Authorization: Bearer`) |
| `BIGHUB_BASE_URL` | No | `https://api.bighub.io` | API base URL |
| `BIGHUB_TIMEOUT_MS` | No | `15000` | HTTP request timeout in milliseconds |
| `BIGHUB_MAX_RETRIES` | No | `2` | Retry count on transient failures (429/5xx) |
| `BIGHUB_ALLOW_INSECURE_HTTP` | No | — | Allow HTTP for localhost/private host testing |

*One of `BIGHUB_API_KEY` or `BIGHUB_BEARER_TOKEN` is required.

---

## Tool coverage

35+ MCP tools mapping one-to-one to BIGHUB API endpoints:

| Domain | Tools | Description |
|--------|-------|-------------|
| **Actions** | submit, submit_v2, dry_run, status, verify, stats, dashboard_summary | Simulate, score, and enforce agent actions before execution. |
| **Future Memory** | ingest, context, refresh_aggregates, recommendations | Ingest decisions, query learned patterns, surface self-improving policy recommendations. |
| **Rules** | create, list, get, update, delete, pause, resume, validate, dry_run, versions, domains, apply_patch, purge_idempotency | Define and manage execution policies that improve over time. |
| **Approvals** | list, resolve | Human-in-the-loop approval workflows. |
| **Kill switch** | status, activate, deactivate | Emergency stop for all agent execution. |
| **Events** | list, stats | Audit trail for scored decisions. |
| **API keys** | create, list, delete, rotate, validate, scopes | Manage authentication credentials. |
| **Webhooks** | create, list, get, update, delete, deliveries, test, list_events, verify_signature, replay | Export decision events to external systems. |
| **Auth** | signup, login, refresh, logout | Account and session management. |
| **Fallback** | `bighub_http_request` | Generic tool for any BIGHUB endpoint not yet wrapped. |

---

## Reliability

- Retries with exponential backoff and jitter for transient errors (429, 5xx, network)
- Configurable timeout per request
- Structured error metadata preserved from API responses
- HTTPS enforced by default (override for local testing only)

---

## Local development

```bash
git clone https://github.com/bighub-io/bighub.git
cd bighub/servers/mcp
npm install
npm run test      # run tests with vitest
npm run check     # typecheck with tsc --noEmit
npm run build     # compile to dist/
npm run start     # run compiled server
npm run dev       # run with tsx (auto-reload)
```

---

## Links

- [bighub.io](https://bighub.io)
- [GitHub — bighub-io/bighub](https://github.com/bighub-io/bighub)
- [npm — @bighub/bighub-mcp](https://www.npmjs.com/package/@bighub/bighub-mcp)
- [PyPI — bighub (Python SDK)](https://pypi.org/project/bighub/)
- [PyPI — bighub-openai](https://pypi.org/project/bighub-openai/)

---

## License

MIT
