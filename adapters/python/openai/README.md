# bighub-openai

> OpenAI adapter for decision learning on tool calls.

`bighub-openai` connects the OpenAI Responses API to BIGHUB so tool calls can be evaluated before execution and learned from after execution.

```text
OpenAI Responses API  ->  bighub-openai  ->  BIGHUB
tool call             ->  evaluate       ->  execute / block / approval
real outcome          ->  report         ->  learn from similar cases
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

guard = BighubOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    bighub_api_key=os.getenv("BIGHUB_API_KEY"),
    actor="AI_AGENT_001",
    domain="customer_transactions",
)

guard.tool(
    "refund_payment",
    refund_payment,
    value_from_args=lambda a: a["amount"],
)

response = guard.run(
    messages=[{"role": "user", "content": "Refund order ord_123 for 199.99"}],
    model="gpt-4.1",
)

print(response["execution"]["last"]["status"])
# executed | blocked | approval_required
```

`guard.tool(...)` auto-generates a strict JSON schema from the Python function signature. Use `parameters_schema=...` only when you need custom constraints.

---

## How It Works

For every tool call, the adapter follows the same loop:

1. The model proposes a tool call
2. The adapter captures action + arguments + actor + domain
3. BIGHUB evaluates the action in context
4. A decision is returned (`allowed`, `blocked`, `requires_approval`)
5. If allowed, the tool executes
6. The action can later be linked to its real outcome
7. Outcome feedback means future similar tool calls are judged with more experience

---

## Response Shape

```python
{
  "llm_response": {...},
  "execution": {
    "events": [...],
    "last": {
      "tool": "refund_payment",
      "status": "executed",   # executed | blocked | approval_required
      "decision": {
        "allowed": True,
        "result": "allowed",
        "reason": "Matched positive outcomes from similar refund decisions",
        "request_id": "act_abc123",
        "requires_approval": False,
        "risk_score": 0.21
      }
    }
  }
}
```

The exact decision payload can include additional backend fields. In most integrations, the key signals are:

- whether execution is allowed now
- whether human approval is required
- how the action was judged from past experience

Decision vs execution naming:

- Decision result: `allowed` / `blocked` / `requires_approval`
- Execution status: `executed` / `blocked` / `approval_required`

---

## Streaming

```python
for event in guard.run_stream(
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
| `execution_event` | Tool decision or execution result |
| `final_response` | Final payload, same shape as `run()` |
| `response_done` | Response finished |
| `response_failed` | Response error |

---

## Async

```python
from bighub_openai import AsyncBighubOpenAI

guard = AsyncBighubOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    bighub_api_key=os.getenv("BIGHUB_API_KEY"),
    actor="AI_AGENT_001",
    domain="customer_transactions",
)

response = await guard.run(
    messages=[{"role": "user", "content": "Refund order ord_123 for 199.99"}],
    model="gpt-4.1",
)
```

---

## Human-in-the-Loop Approvals

```python
result = guard.run_with_approval(
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
