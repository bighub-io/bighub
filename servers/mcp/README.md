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

## Typical MCP Loop

1. Submit a decision for evaluation
2. Receive a recommendation and decision signals
3. Let the agent or runtime act
4. Report the real outcome
5. Inspect similar past cases and calibration
6. Use what was learned on the next decision

```text
bighub_actions_evaluate
→ agent runtime acts based on recommendation
→ bighub_outcomes_report
→ bighub_precedents_query
→ bighub_calibration_report
→ bighub_insights_advise
```

---

## Structured recommendation

Every evaluation returns a structured recommendation — not just allow / block:

| Field | Description |
|---|---|
| `recommendation` | `proceed`, `proceed_with_caution`, `review_recommended`, `do_not_proceed` |
| `recommendation_confidence` | `high`, `medium`, `low` |
| `risk_score` | Aggregated risk (0–1) |
| `enforcement_mode` | `advisory`, `review`, `enforced` |
| `decision_intelligence` | Rationale, evidence status, trajectory health, alternatives |

Legacy fields (`allowed`, `result`, `reason`) may still appear for backward compatibility but are not the primary surface.

---

## Trajectory-aware evaluation

BIGHUB evaluates actions not only in isolation, but also in the context of what happened before. As outcomes accumulate, similar sequences and prior decisions improve future recommendations.

---

## Complete Tool Reference

125 tools organized by domain. The core loop tools are listed first.

### Core loop

| Tool | Description |
|---|---|
| `bighub_actions_evaluate` | Submit an action for evaluation — returns recommendation, confidence, risk score |
| `bighub_outcomes_report` | Report what actually happened after execution |
| `bighub_precedents_query` | Query similar past cases |
| `bighub_calibration_report` | Calibration report (prediction vs reality) |
| `bighub_insights_advise` | Learned advisories for an action |

### Actions

| Tool | Description |
|---|---|
| `bighub_actions_evaluate` | Evaluate an action (primary entry point) |
| `bighub_actions_evaluate_payload` | Evaluate with a free-form payload |
| `bighub_actions_evaluate_batch` | Evaluate multiple actions in one request |
| `bighub_actions_dry_run` | Non-persistent evaluation (preview) |
| `bighub_actions_live_connect` | Open a live connection slot |
| `bighub_actions_live_heartbeat` | Heartbeat a live connection |
| `bighub_actions_live_disconnect` | Close a live connection |
| `bighub_actions_verify_validation` | Verify a validation hash |
| `bighub_actions_observer_stats` | Observer statistics |
| `bighub_actions_dashboard_summary` | Dashboard summary metrics |
| `bighub_actions_status` | Service status |
| `bighub_actions_memory_ingest` | Ingest decision memory events |
| `bighub_actions_memory_context` | Retrieve memory context |
| `bighub_actions_memory_refresh_aggregates` | Refresh memory aggregates |
| `bighub_actions_memory_recommendations` | Pattern-based recommendations from memory |

### Outcomes

| Tool | Description |
|---|---|
| `bighub_outcomes_report` | Report a real-world outcome |
| `bighub_outcomes_report_batch` | Batch report outcomes |
| `bighub_outcomes_get` | Get outcome by request_id |
| `bighub_outcomes_get_by_validation` | Get outcome by validation_id |
| `bighub_outcomes_get_by_case` | Get outcome by case_id |
| `bighub_outcomes_timeline` | Full outcome timeline |
| `bighub_outcomes_pending` | Decisions awaiting outcomes |
| `bighub_outcomes_analytics` | Outcome analytics summary |
| `bighub_outcomes_taxonomy` | Supported outcome statuses |
| `bighub_outcomes_recommendation_quality` | Follow rate, quadrants, trend, by domain/actor |
| `bighub_outcomes_partner_view` | Self-contained domain view with KPIs and examples |

### Decision cases

| Tool | Description |
|---|---|
| `bighub_cases_create` | Create a decision case |
| `bighub_cases_get` | Get a case by ID |
| `bighub_cases_list` | List and filter cases |
| `bighub_cases_report_outcome` | Report outcome for a case |
| `bighub_cases_precedents` | Precedent intelligence for a proposed action |
| `bighub_cases_calibration` | Calibration metrics for cases |

### Precedents

| Tool | Description |
|---|---|
| `bighub_precedents_query` | Query similar past cases |
| `bighub_precedents_signals` | Aggregated precedent signals |
| `bighub_precedents_stats` | Precedent index statistics |

### Calibration

| Tool | Description |
|---|---|
| `bighub_calibration_report` | Calibration report |
| `bighub_calibration_reliability` | Reliability diagram data |
| `bighub_calibration_drift` | Calibration drift over time |
| `bighub_calibration_breakdown` | Breakdown by domain or tool |
| `bighub_calibration_feedback` | Calibration feedback signals |
| `bighub_calibration_observe` | Submit a calibration observation |
| `bighub_calibration_quality_history` | Daily quality score over time |

### Multi-signal retrieval

| Tool | Description |
|---|---|
| `bighub_retrieval_query` | Multi-signal precedent retrieval |
| `bighub_retrieval_query_explained` | Retrieval with explanation trace |
| `bighub_retrieval_strategies` | List available strategies |
| `bighub_retrieval_strategy` | Get one strategy's details |
| `bighub_retrieval_index_case` | Manually index a case |
| `bighub_retrieval_compare` | Compare two strategies |
| `bighub_retrieval_stats` | Retrieval index statistics |

### Insights

| Tool | Description |
|---|---|
| `bighub_insights_advise` | Learned advisories for an action |
| `bighub_insights_patterns` | Discovered risk patterns |
| `bighub_insights_learn` | Learning refresh |
| `bighub_insights_profile` | Action/tool profile |

### Simulations

| Tool | Description |
|---|---|
| `bighub_simulations_list` | List simulation snapshots |
| `bighub_simulations_get` | Get a snapshot |
| `bighub_simulations_by_request` | Get snapshot by request |
| `bighub_simulations_compare` | Compare predicted vs actual |
| `bighub_simulations_accuracy` | Domain-level accuracy |
| `bighub_simulations_stats` | Simulation statistics |

### Learning

| Tool | Description |
|---|---|
| `bighub_learning_strategy` | Current learning strategy |
| `bighub_learning_runs` | Recent learning runs |
| `bighub_learning_recompute` | Trigger learning recomputation |
| `bighub_learning_backfill` | Backfill learning artifacts |

### Features

| Tool | Description |
|---|---|
| `bighub_features_compute` | Compute features for an action |
| `bighub_features_compute_batch` | Batch feature computation |
| `bighub_features_snapshot` | Create a feature snapshot |
| `bighub_features_get_snapshot` | Get a snapshot |
| `bighub_features_list_snapshots` | List snapshots |
| `bighub_features_explain` | Explain features for a case |
| `bighub_features_export` | Export features for a case |
| `bighub_features_export_batch` | Batch export |
| `bighub_features_compare` | Compare feature sets |
| `bighub_features_schema` | Feature schema |
| `bighub_features_stats` | Feature statistics |

### Runtime ingestion

| Tool | Description |
|---|---|
| `bighub_ingest_event` | Ingest a single event |
| `bighub_ingest_batch` | Ingest events in batch |
| `bighub_ingest_reconcile` | Reconcile outcome with event |
| `bighub_ingest_lifecycles` | List event lifecycles |
| `bighub_ingest_lifecycle` | Get lifecycle for one event |
| `bighub_ingest_pending` | Events pending reconciliation |
| `bighub_ingest_stale` | Stale unreconciled events |
| `bighub_ingest_stats` | Ingestion statistics |
| `bighub_ingest_adapters` | List available adapters |

### Operating constraints

| Tool | Description |
|---|---|
| `bighub_constraints_create` | Create a constraint |
| `bighub_constraints_list` | List constraints |
| `bighub_constraints_get` | Get a constraint |
| `bighub_constraints_update` | Update a constraint |
| `bighub_constraints_delete` | Delete a constraint |
| `bighub_constraints_pause` | Pause a constraint |
| `bighub_constraints_resume` | Resume a constraint |
| `bighub_constraints_dry_run` | Preview without persisting |
| `bighub_constraints_validate` | Validate an action against constraints |
| `bighub_constraints_validate_dry_run` | Validate (dry run) |
| `bighub_constraints_domains` | List domains with constraints |
| `bighub_constraints_versions` | Constraint version history |
| `bighub_constraints_apply_patch` | Apply a JSON Patch |
| `bighub_constraints_purge_idempotency` | Admin: purge idempotency keys |

### Approvals & kill switch

| Tool | Description |
|---|---|
| `bighub_approvals_list` | List approval requests |
| `bighub_approvals_resolve` | Resolve an approval |
| `bighub_kill_switch_status` | Kill switch status |
| `bighub_kill_switch_activate` | Activate kill switch |
| `bighub_kill_switch_deactivate` | Deactivate kill switch |

### Events

| Tool | Description |
|---|---|
| `bighub_events_list` | Query event stream |
| `bighub_events_stats` | Event statistics |

### Webhooks

| Tool | Description |
|---|---|
| `bighub_webhooks_create` | Create a webhook |
| `bighub_webhooks_list` | List webhooks |
| `bighub_webhooks_get` | Get a webhook |
| `bighub_webhooks_update` | Update a webhook |
| `bighub_webhooks_delete` | Delete a webhook |
| `bighub_webhooks_deliveries` | List deliveries |
| `bighub_webhooks_test` | Send a test delivery |
| `bighub_webhooks_list_events` | List subscribable event types |
| `bighub_webhooks_verify_signature` | Verify webhook signature |
| `bighub_webhooks_replay_failed_delivery` | Replay a failed delivery |

### API keys

| Tool | Description |
|---|---|
| `bighub_api_keys_create` | Create an API key |
| `bighub_api_keys_list` | List API keys |
| `bighub_api_keys_delete` | Delete an API key |
| `bighub_api_keys_rotate` | Rotate an API key |
| `bighub_api_keys_validate` | Validate an API key |
| `bighub_api_keys_scopes` | List available scopes |

### Auth

| Tool | Description |
|---|---|
| `bighub_auth_signup` | Create an account |
| `bighub_auth_login` | Log in |
| `bighub_auth_refresh` | Refresh token |
| `bighub_auth_logout` | Log out |

### Utility

| Tool | Description |
|---|---|
| `bighub_http_request` | Generic HTTP passthrough |

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

Management tools (API keys, webhooks, auth) require user JWT auth via `BIGHUB_BEARER_TOKEN`.

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
