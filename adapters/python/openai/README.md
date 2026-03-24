# bighub-openai

> OpenAI adapter for decision learning on tool calls.

`bighub-openai` connects the OpenAI Responses API to BIGHUB so tool calls are evaluated before execution, receive structured recommendations, and learn from real outcomes.

```text
OpenAI Responses API  →  bighub-openai          →  BIGHUB
tool call             →  evaluate                →  recommendation + confidence + rationale
agent / runtime acts  →  execution or escalation
real outcome          →  report                  →  future recommendations improve
```

---

## Install

```bash
pip install bighub-openai
```

Requires Python 3.9+.

Dependencies:

- `bighub>=3.0.0,<4.0.0`
- `openai>=2.0.0,<3.0.0`

---

## Quickstart

```python
import os
from bighub_openai import BighubOpenAI

def refund_payment(order_id: str, amount: float) -> dict:
    return {"ok": True, "order_id": order_id, "amount": amount}

runtime = BighubOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    bighub_api_key=os.getenv("BIGHUB_API_KEY"),
    actor="AI_AGENT_001",
    domain="customer_transactions",
)

runtime.tool(
    "refund_payment",
    refund_payment,
    value_from_args=lambda a: a["amount"],
)

response = runtime.run(
    messages=[{"role": "user", "content": "Refund order ord_123 for 199.99"}],
    model="gpt-4.1",
)

print(response["execution"]["last"]["status"])
# executed | blocked | approval_required
```

`runtime.tool(...)` auto-generates a strict JSON schema from the Python function signature. Use `parameters_schema=...` only when you need custom constraints.

---

## How It Works

For every tool call, the adapter follows the same loop:

1. The model proposes a tool call
2. The adapter captures action, arguments, actor, and domain
3. BIGHUB evaluates the action in context
4. A structured recommendation is returned
5. The adapter decides how to handle execution based on mode:
   - **advisory** — surfaces the recommendation; the agent executes by default
   - **review** — requires approval or escalation before execution
   - **enforced** — applies runtime constraints when configured
6. The action can later be linked to its real outcome
7. Outcome feedback means future similar tool calls receive better recommendations

---

## Response Shape

```python
{
  "llm_response": {...},
  "execution": {
    "events": [...],
    "last": {
      "tool": "refund_payment",
      "status": "executed",
      "decision": {
        "recommendation": "proceed_with_caution",
        "recommendation_confidence": "medium",
        "risk_score": 0.21,
        "enforcement_mode": "advisory",
        "decision_intelligence": {
          "rationale": "Matched positive outcomes from similar refund decisions",
          "evidence_status": "sufficient",
          "trajectory_health": "healthy"
        },
        "request_id": "act_abc123"
      }
    }
  }
}
```

The primary decision signals are:

- `recommendation` — what BIGHUB recommends (`proceed`, `proceed_with_caution`, `review_recommended`, `do_not_proceed`)
- `recommendation_confidence` — confidence level (`high`, `medium`, `low`)
- `risk_score` — aggregated risk (0–1)
- `enforcement_mode` — how the recommendation is applied (`advisory`, `review`, `enforced`)
- `decision_intelligence` — rationale, evidence status, trajectory health

Legacy fields such as `allowed`, `result`, and `reason` may still be present for backward compatibility, but they are not the primary product surface.

---

## Streaming

```python
for event in runtime.run_stream(
    messages=[{"role": "user", "content": "Refund order ord_123 for 199.99"}],
    model="gpt-4.1",
):
    if event["type"] == "llm_delta":
        print(event["delta"], end="")
    elif event["type"] == "execution_event":
        print("\n[decision]", event["event"]["tool"], event["event"]["status"])
    elif event["type"] == "final_response":
        print("\nDone:", event["response"]["output_text"])
```

| Event type | Description |
|---|---|
| `llm_delta` | Incremental text token |
| `llm_text_done` | Complete text segment |
| `execution_event` | Tool recommendation and execution result |
| `final_response` | Final payload, same shape as `run()` |
| `response_done` | Response finished |
| `response_failed` | Response error |

---

## Async

```python
from bighub_openai import AsyncBighubOpenAI

runtime = AsyncBighubOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    bighub_api_key=os.getenv("BIGHUB_API_KEY"),
    actor="AI_AGENT_001",
    domain="customer_transactions",
)

response = await runtime.run(
    messages=[{"role": "user", "content": "Refund order ord_123 for 199.99"}],
    model="gpt-4.1",
)
```

---

## Human-in-the-Loop Approvals

```python
result = runtime.run_with_approval(
    messages=[{"role": "user", "content": "Refund order ord_123 for 5000"}],
    model="gpt-4.1",
    on_approval_required=lambda ctx: {
        "resolution": "approved",
        "comment": "approved by on-call",
    },
)
```

Run approval callbacks server-side, not in clients, to avoid exposing approval credentials.

---

## Links

- [bighub.io](https://bighub.io)
- [GitHub — bighub-io/bighub](https://github.com/bighub-io/bighub)
- [PyPI — bighub-openai](https://pypi.org/project/bighub-openai/)
- [PyPI — bighub](https://pypi.org/project/bighub/)

---

## License

MIT
