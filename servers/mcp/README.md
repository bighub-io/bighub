# bighub-mcp

Official MCP server for BIGHUB governance APIs.

This package exposes MCP tools that call `https://api.bighub.io` for governance operations:
actions, rules, approvals, kill switch, events, API keys, webhooks, and auth.

## Install

```bash
npm install bighub-mcp
```

## Local development

```bash
npm install
npm run test
npm run check
npm run build
```

Run in stdio mode:

```bash
npm run start
```

## Environment variables

- `BIGHUB_API_KEY` - preferred auth method (`X-API-Key`)
- `BIGHUB_BEARER_TOKEN` - optional auth method (`Authorization: Bearer ...`)
- `BIGHUB_BASE_URL` - defaults to `https://api.bighub.io`
- `BIGHUB_TIMEOUT_MS` - HTTP timeout (default: `15000`)
- `BIGHUB_MAX_RETRIES` - retry count on transient failures (default: `2`)
- `BIGHUB_ALLOW_INSECURE_HTTP` - only for localhost/private host testing

## Tool coverage

- **Actions:** submit, submit_v2, dry_run, status, verify, stats, dashboard summary
- **Future Memory:** ingest, context, refresh aggregates, recommendations
- **Rules:** create/list/get/update/delete/pause/resume/validate/dry-run/versions/domains/apply_patch/purge_idempotency
- **Approvals:** list, resolve
- **Kill switch:** status, activate, deactivate
- **Events:** list, stats
- **API keys:** create, list, delete, rotate, validate, scopes
- **Webhooks:** create, list, get, update, delete, deliveries, test, list_events, verify_signature, replay
- **Auth:** signup, login, refresh, logout
- **Fallback:** generic `bighub_http_request` tool for endpoints not yet wrapped

## Notes

- Tools are one-to-one wrappers over BIGHUB HTTP endpoints.
- Retries use exponential backoff with jitter for transient errors.
- Errors preserve structured metadata when returned by the API.

## Links

- [Main README](../../README.md)
