# @bighub/bighub-mcp

> MCP server for decision learning on agent actions.

Use BIGHUB from any [Model Context Protocol](https://modelcontextprotocol.io) client to evaluate agent actions, receive structured recommendations, report real outcomes, and improve future decisions over time.

```text
MCP client
   ↓
@bighub/bighub-mcp
   ↓
BIGHUB API
   ↓
evaluate → recommend → agent acts → report outcome → learn
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
| `bighub_actions_submit` | Submit an action for evaluation — returns recommendation, confidence, risk score |
| `bighub_outcomes_report` | Report what actually happened after execution |
| `bighub_precedents_query` | Retrieve similar past cases to inform the next decision |
| `bighub_calibration_report` | Compare prediction vs reality |
| `bighub_insights_advise` | Retrieve learned guidance for the next action |
| `bighub_outcomes_recommendation_quality` | Recommendation quality analytics: follow rate, quadrants, trend |
| `bighub_outcomes_partner_view` | Self-contained per-domain view: KPIs, examples, evidence pockets |

`bighub_actions_evaluate_payload` is available as an advanced action evaluation endpoint.

---

## Typical MCP Loop

1. Submit a decision for evaluation
2. Receive a recommendation and decision signals
3. Let the agent or runtime act
4. Report the real outcome
5. Inspect similar past cases and calibration
6. Use what was learned on the next decision

Typical tool flow:

```text
bighub_actions_submit
→ agent runtime acts based on recommendation
→ bighub_outcomes_report
→ bighub_precedents_query
→ bighub_calibration_report
→ bighub_insights_advise
```

---

## Structured recommendation

BIGHUB primarily returns:

- `recommendation` — what to do (`proceed`, `proceed_with_caution`, `review_recommended`, `do_not_proceed`)
- `recommendation_confidence` — how confident (`high`, `medium`, `low`)
- `risk_score` — aggregated risk (0–1)
- `enforcement_mode` — how the recommendation is applied (`advisory`, `review`, `enforced`)
- `decision_intelligence` — rationale, evidence status, trajectory health, alternatives

Legacy fields such as `allowed`, `result`, and `reason` may still appear for backward compatibility, but they are not the primary product surface.

---

## Trajectory-aware evaluation

BIGHUB evaluates actions not only in isolation, but also in the context of what happened before. As outcomes accumulate, similar sequences and prior decisions improve future recommendations.

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
