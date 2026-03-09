# BIGHUB

> Execution governance for autonomous AI agents.

AI agents no longer just suggest — they act. They modify data, trigger payments, call external systems. When an agent acts outside its intended boundaries, the impact is immediate.

BIGHUB sits between agent reasoning and real-world execution. Every action is validated against explicit policies before it runs.

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

## What BIGHUB does

| Without BIGHUB | With BIGHUB |
|---|---|
| Agent acts directly in production | Every action validated before execution |
| Guardrails are suggestions | Policies are enforced at runtime |
| Logs show what happened | Decisions are blocked before they happen |
| Autonomy grows, exposure grows | Bounded autonomy, controlled risk |

---

## Core concepts

**Domains** — Scope your policies by execution context:

- `financial_actions`
- `operational_systems`
- `infrastructure_devops`
- `customer_transactions`
- `data_modifications`
- `custom`

**Policy rules** — Define limits per domain: max value, max per day, approval threshold, behavioral constraints.

**Decision outcomes** — Every submitted action returns:
- `allowed: true/false`
- `risk_score: 0.0–1.0`
- `blocked_by` (if blocked)

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
# Ingest governed execution events
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

# Query learned context
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

# Preview then apply with optimistic locking
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

## Reliability

- Configurable timeout
- Retry with exponential backoff (429 / 5xx / network errors)
- Idempotency-Key support on mutable endpoints
- Typed exception hierarchy with request/response metadata

---

## Provider adapters

| Adapter | Status |
|---|---|
| `bighub-openai` | ✅ Available |
| `bighub-anthropic` | 🔜 Coming soon |
| `bighub-perplexity` | 🔜 Coming soon |

```bash
pip install bighub-openai
```

→ See [bighub-openai on PyPI](https://pypi.org/project/bighub-openai/)

---

## Auth

```python
# API key (recommended)
client = BighubClient(api_key="...")

# Bearer token
client = BighubClient(bearer_token="...")
```

---

## Links

- [PyPI — bighub](https://pypi.org/project/bighub/)
- [PyPI — bighub-openai](https://pypi.org/project/bighub-openai/)
- [bighub.io](https://bighub.io)

---

## License

MIT
