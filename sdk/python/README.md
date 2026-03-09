# BIGHUB — AI Agent Control Plane

> Official Python SDK for governing AI agent execution with the BIGHUB control plane.

BIGHUB is the execution control plane for AI agents in production. It sits between agent reasoning and real-world execution, validating every action against enforceable policies before it reaches production systems.

As AI agents move from suggestion to execution, risk becomes structural. BIGHUB makes autonomy enforceable.

```text
LLM / Agent Runtime
        ↓
Provider Adapter (e.g. bighub-openai)
        ↓
BIGHUB Control Plane API
        ↓
Rules + Approvals + Memory + Policy Intelligence
        ↓
execute / block / require approval
```

---

## Install

```bash
pip install bighub
```

Requires Python 3.9+.

---

## Quickstart

```python
import os
from bighub import BighubClient

client = BighubClient(api_key=os.getenv("BIGHUB_API_KEY"))

result = client.actions.submit(
    action="update_price",
    value=150.0,
    domain="financial_actions",
    actor="AI_AGENT_001",
)

print(result["allowed"], result["risk_score"])
# True, 0.12
client.close()
```

Async:

```python
import asyncio, os
from bighub import AsyncBighubClient

async def main():
    async with AsyncBighubClient(api_key=os.getenv("BIGHUB_API_KEY")) as client:
        result = await client.actions.submit(
            action="update_price",
            value=150.0,
            domain="financial_actions",
            actor="AI_AGENT_001",
        )
        print(result["allowed"], result["risk_score"])

asyncio.run(main())
```

---

## Why BIGHUB?

| Without BIGHUB | With BIGHUB |
|---|---|
| Agent acts directly in production | Every action validated before execution |
| Guardrails are suggestions | Policies are enforced at runtime |
| Logs show what happened | Decisions are blocked before they happen |
| Autonomy grows, exposure grows | Bounded autonomy, controlled risk |

---

## Core concepts

**Execution domains** — Scope policies by context:
`financial_actions`, `operational_systems`, `infrastructure_devops`, `customer_transactions`, `data_modifications`, `custom`.

**Policy rules** — Define limits per domain: max value, max per day, approval threshold, behavioral constraints.

**Decision outcomes** — Every submitted action returns: `allowed`, `risk_score`, `blocked_by`.

**Approvals** — Actions above defined thresholds are held for human review before execution.

**Kill switch** — Instantly stop all agent execution, globally or per domain.

---

## Policy rules

```python
from bighub import BighubClient, RuleCreateModel

client = BighubClient(api_key=os.getenv("BIGHUB_API_KEY"))

rule = client.rules.create(
    RuleCreateModel(
        name="Pricing Safety Rule",
        domain="financial_actions",
        max_per_day=100,
        max_value=1000,
        require_approval_above=500,
    )
)
```

---

## Future Memory

BIGHUB learns from governed execution. Over time, it detects patterns and surfaces safe policy recommendations — without ever loosening autonomy automatically.

```python
client.actions.ingest_memory(
    source="openai_adapter",
    actor="AI_AGENT_001",
    domain="customer_transactions",
    events=[
        {
            "event_id": "6f1aa3f4-...",
            "tool": "refund_payment",
            "status": "blocked",
            "decision": {"allowed": False, "blocked_by": "max_value", "risk_score": 0.91},
            "arguments": {"order_id": "ord_123", "amount": 2500.0},
        }
    ],
)

context = client.actions.memory_context(window_hours=24, tool="refund_payment")
print(context["blocked_rate"], context["top_block_reasons"])
```

Policy recommendations (Pro/Enterprise):

```python
recommendations = client.actions.memory_recommendations(
    window_hours=24,
    scope={"domain": "customer_transactions", "tool": "refund_payment"},
    min_events=20,
    auto_apply=False,
)

rec = recommendations["recommendations"][0]
preview = client.rules.apply_patch(rec["target_rule_id"], patch=rec["suggested_policy_patch"], preview=True)
client.rules.apply_patch(rec["target_rule_id"], patch=rec["suggested_policy_patch"], preview=False, if_match_version=preview["after"]["version"])
```

> Future Memory is experimental and may contain bugs.

---

## Approvals

```python
pending = client.approvals.list(status_filter="pending")

client.approvals.resolve(
    pending[0]["request_id"],
    resolution="approved",
    comment="approved by on-call",
)
```

---

## Kill switch

```python
client.kill_switch.activate()   # stop everything
client.kill_switch.deactivate() # resume
```

---

## Webhooks

```python
client.webhooks.create({
    "url": "https://yourapp.com/webhooks/bighub",
    "label": "prod-endpoint",
    "events": ["decision_event.created", "approval.created"],
})
```

---

## Supported domains

| Resource | Operations |
|---|---|
| **actions** | submit, submit_v2, dry_run, verify_validation, observer_stats, dashboard_summary, status, ingest_memory, memory_context, refresh_memory_aggregates, memory_recommendations |
| **rules** | create, list, get, update, delete, pause, resume, apply_patch, dry_run, validate, validate_dry_run, domains, versions, purge_idempotency |
| **approvals** | list, resolve |
| **kill_switch** | status, activate, deactivate |
| **events** | list, stats |
| **api_keys** | create, list, delete/revoke, rotate, validate, scopes |
| **webhooks** | create, list, get, update, delete, deliveries, test, list_events, verify_signature, replay_failed_delivery |
| **auth** | signup, login, refresh, logout |

---

## Reliability

- Configurable timeout
- Retry with exponential backoff (429 / 5xx / network errors)
- Idempotency-Key support on mutable endpoints
- Typed exception hierarchy with request/response metadata

---

## Provider adapters

| Adapter | Status |
|---|---|
| `bighub-openai` | Available |
| `bighub-anthropic` | Coming soon |
| `bighub-perplexity` | Coming soon |

```bash
pip install bighub-openai
```

---

## Auth

```python
client = BighubClient(api_key="...")       # X-API-Key (recommended)
client = BighubClient(bearer_token="...")   # Authorization: Bearer
```

---

## Links

- [bighub.io](https://bighub.io)
- [GitHub — bighub-io/bighub](https://github.com/bighub-io/bighub)
- [PyPI — bighub](https://pypi.org/project/bighub/)
- [PyPI — bighub-openai](https://pypi.org/project/bighub-openai/)
- [npm — @bighub/bighub-mcp](https://www.npmjs.com/package/@bighub/bighub-mcp)

---

## License

MIT
