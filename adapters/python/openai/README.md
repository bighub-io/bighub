# bighub-openai

> Production-safe OpenAI agents with execution governance.

`bighub-openai` wraps the OpenAI Responses API with BIGHUB governance. Before any tool executes, BIGHUB validates it against your policies — and blocks or escalates if boundaries are exceeded.

```text
OpenAI Responses API  →  bighub-openai  →  BIGHUB Control Plane  →  execute / block / approve
```

---

## Install

```bash
pip install bighub-openai
```

Requires Python 3.9+. Depends on `bighub>=0.2.6` and `openai>=2.0.0,<3.0.0`.

---

## Quickstart

```python
import os
from bighub_openai import GuardedOpenAI

def refund_payment(order_id: str, amount: float) -> dict:
    return {"ok": True, "order_id": order_id, "amount": amount}

guard = GuardedOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    bighub_api_key=os.getenv("BIGHUB_API_KEY"),
    actor="AI_AGENT_001",
    domain="customer_transactions",
)

guard.tool("refund_payment", refund_payment, value_from_args=lambda a: a["amount"])

response = guard.run(
    messages=[{"role": "user", "content": "Refund order ord_123 for 199.99"}],
    model="gpt-4.1",
)

print(response["execution"]["last"]["status"])
# executed | blocked | approval_required
```

---

## How it works

For every tool call, the adapter:

1. Intercepts the tool call before execution
2. Submits the action to BIGHUB for policy validation
3. If `allowed` → executes the tool
4. If `blocked` → does not execute, returns decision context
5. If `requires_approval` → holds execution, returns `approval_required`

Tool schema is auto-generated from your Python function signature — no manual JSON schema needed.

---

## Response shape

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
        "risk_score": 0.21,
      }
    }
  }
}
```

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
        print("\n[governance]", event["event"]["tool"], event["event"]["status"])
    elif event["type"] == "final_response":
        print("\nDone:", event["response"]["output_text"])
```

| Event type | Description |
|---|---|
| `llm_delta` | Incremental text token |
| `llm_text_done` | Complete text segment |
| `execution_event` | Governed tool decision/result |
| `final_response` | Final payload (same shape as `run()`) |
| `response_done` | Response finished |
| `response_failed` | Response error |

---

## Async

```python
from bighub_openai import AsyncGuardedOpenAI

guard = AsyncGuardedOpenAI(
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

## Human-in-the-loop approvals

When an action exceeds your approval threshold, execution is held until resolved.

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

> Run approval callbacks server-side — not in the client — to avoid exposing approval credentials.

---

## Audit hook

Forward every governed decision to your observability stack:

```python
def log_decision(event: dict) -> None:
    print({
        "trace_id": event.get("trace_id"),
        "allowed": event.get("allowed"),
        "tool": event.get("tool"),
    })

guard = GuardedOpenAI(..., on_decision=log_decision)
```

---

## Silent mode

Evaluate governance without executing tools:

```python
decision = guard.check_tool("refund_payment", {"order_id": "ord_123", "amount": 199.0})
print(decision["allowed"], decision["risk_score"])
```

---

## Fail modes

```python
# Default: if policy check fails unexpectedly, block execution
guard = GuardedOpenAI(..., fail_mode="closed")

# Open: if policy check fails unexpectedly, allow execution
guard = GuardedOpenAI(..., fail_mode="open")
```

---

## Provider resilience

```python
guard = GuardedOpenAI(
    ...,
    provider_timeout_seconds=20,
    provider_max_retries=3,
    provider_retry_backoff_seconds=0.2,
    provider_retry_max_backoff_seconds=2.0,
    provider_circuit_breaker_failures=5,
    provider_circuit_breaker_reset_seconds=30,
)
```

Retries only trigger on transient OpenAI errors (`APIConnectionError`, `APITimeoutError`, `RateLimitError`). Non-retryable errors fail immediately.

---

## Future Memory

The adapter ingests governed execution events into BIGHUB Future Memory by default — powering pattern detection and policy recommendations over time.

```python
guard = GuardedOpenAI(..., memory_enabled=True)
```

Memory ingest is best-effort: short timeout, exceptions swallowed, governance path never blocked by telemetry.

> Future Memory is experimental and may contain bugs.

---

## Links

- [PyPI — bighub-openai](https://pypi.org/project/bighub-openai/)
- [PyPI — bighub (core SDK)](https://pypi.org/project/bighub/)
- [bighub.io](https://bighub.io)

---

## License

MIT
