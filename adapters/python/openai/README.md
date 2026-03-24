# bighub-openai

> OpenAI adapter for decision learning on tool calls.

`bighub-openai` connects the OpenAI Responses API to BIGHUB so tool calls are evaluated before execution, receive structured recommendations, and learn from real outcomes automatically.

```text
OpenAI Responses API  →  bighub-openai          →  BIGHUB
tool call             →  evaluate                →  recommendation + confidence + rationale
agent / runtime acts  →  execution or escalation
real outcome          →  report (automatic)      →  future recommendations improve
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

last = response["execution"]["last"]
print(last["decision"]["recommendation"])             # proceed, proceed_with_caution, review_recommended, do_not_proceed
print(last["decision"]["recommendation_confidence"])   # high, medium, low
print(last["decision"]["risk_score"])                  # 0.0 – 1.0
print(last["status"])                                  # executed, blocked, approval_required
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
6. If the tool executes, the outcome is automatically reported back to BIGHUB
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

### Primary decision signals

| Field | Description |
|---|---|
| `recommendation` | `proceed`, `proceed_with_caution`, `review_recommended`, `do_not_proceed` |
| `recommendation_confidence` | `high`, `medium`, `low` |
| `risk_score` | Aggregated risk (0–1) |
| `enforcement_mode` | `advisory`, `review`, `enforced` |
| `decision_intelligence` | Rationale, evidence status, trajectory health, alternatives |

### Execution statuses

| Status | Description |
|---|---|
| `executed` | Tool ran successfully |
| `blocked` | BIGHUB or runtime prevented execution |
| `approval_required` | Waiting for human approval |
| `tool_error` | Tool raised an exception during execution |

Legacy fields such as `allowed`, `result`, and `reason` may still be present for backward compatibility, but they are not the primary product surface.

---

## Configuration

### Constructor parameters

```python
runtime = BighubOpenAI(
    # Required
    bighub_api_key="bh_live_xxx",
    actor="AI_AGENT_001",
    domain="customer_transactions",

    # OpenAI (one of these is required)
    openai_api_key="sk-xxx",           # or pass your own client:
    openai_client=my_openai_client,    # pre-configured OpenAI() instance

    # Decision behavior
    decision_mode="submit",            # "submit" (default) or "submit_payload"
    fail_mode="closed",                # "closed" = block on BIGHUB errors, "open" = allow on errors
    max_tool_rounds=8,                 # max consecutive tool call rounds

    # Outcome & memory (automatic)
    outcome_reporting=True,            # auto-report tool execution results
    memory_enabled=True,               # ingest decision memory events
    on_decision=my_callback,           # called after each BIGHUB decision

    # Provider resilience
    provider_timeout_seconds=30.0,
    provider_max_retries=2,
    provider_retry_backoff_seconds=0.25,
    provider_circuit_breaker_failures=0,   # 0 = disabled
    evaluate_retries=2,
)
```

### `fail_mode`

| Mode | Behavior when BIGHUB is unreachable |
|---|---|
| `closed` (default) | Block execution — fail safe |
| `open` | Allow execution — fail open |

---

## Registering tools

### Basic

```python
runtime.tool("send_email", send_email)
```

### With value and target extraction

```python
runtime.tool(
    "transfer_funds",
    transfer_funds,
    value_from_args=lambda a: a["amount"],
    target_from_args=lambda a: a["recipient_id"],
)
```

### Per-tool overrides

```python
runtime.tool(
    "delete_account",
    delete_account,
    domain="account_management",       # override adapter-level domain
    actor="admin_agent",               # override adapter-level actor
    action_name="account_deletion",    # custom action name for BIGHUB
    decision_mode="submit_payload",    # per-tool decision mode
    metadata_from_args=lambda a: {"priority": "high"},
)
```

### Custom JSON schema

```python
runtime.tool(
    "approve_loan",
    approve_loan,
    parameters_schema={
        "type": "object",
        "properties": {
            "loan_id": {"type": "string"},
            "amount": {"type": "number", "minimum": 0},
        },
        "required": ["loan_id", "amount"],
        "additionalProperties": False,
    },
    strict=True,
)
```

### Full API: `register_tool()`

```python
runtime.register_tool(
    name="refund_payment",
    fn=refund_payment,
    description="Process a customer refund",
    parameters_schema={...},
    value_from_args=lambda a: a["amount"],
    target_from_args=lambda a: a["order_id"],
    action_name="refund",
    domain="payments",
    actor="refund_bot",
    metadata_from_args=lambda a: {"source": "support_ticket"},
    decision_mode="submit",
    strict=True,
)
```

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

async with AsyncBighubOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    bighub_api_key=os.getenv("BIGHUB_API_KEY"),
    actor="AI_AGENT_001",
    domain="customer_transactions",
) as runtime:
    runtime.tool("refund_payment", refund_payment, value_from_args=lambda a: a["amount"])

    response = await runtime.run(
        messages=[{"role": "user", "content": "Refund order ord_123 for 199.99"}],
        model="gpt-4.1",
    )

    # Async streaming
    async for event in runtime.run_stream(
        messages=[{"role": "user", "content": "Refund order ord_456"}],
        model="gpt-4.1",
    ):
        if event["type"] == "llm_delta":
            print(event["delta"], end="")
```

---

## Human-in-the-loop approvals

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

When BIGHUB returns `requires_approval`, the adapter pauses execution and calls `on_approval_required` with the decision context. Return `{"resolution": "approved"}` to resume execution, or `{"resolution": "denied"}` to block it.

Run approval callbacks server-side, not in clients, to avoid exposing approval credentials.

---

## Automatic outcome reporting

When `outcome_reporting=True` (default), the adapter automatically reports:

- **Successful execution** → `SUCCESS` outcome with tool output
- **Blocked execution** → `BLOCKED` outcome
- **Tool errors** → `FAILURE` outcome with error details

This closes the learning loop without manual instrumentation. Disable with `outcome_reporting=False` if you report outcomes manually via the SDK.

---

## Decision memory

When `memory_enabled=True` (default), the adapter ingests structured events (tool calls, decisions, outcomes) into BIGHUB's decision memory. This enables pattern detection and context-aware recommendations across sessions.

---

## Context manager

```python
with BighubOpenAI(...) as runtime:
    runtime.tool("refund_payment", refund_payment)
    response = runtime.run(...)
# BIGHUB client is automatically closed
```

---

## API Reference

### `BighubOpenAI` / `AsyncBighubOpenAI`

| Method | Description |
|---|---|
| `tool(name, fn, **kwargs)` | Register a tool (shorthand for `register_tool`) |
| `register_tool(name, fn, description, parameters_schema, ...)` | Register a tool with full options |
| `list_tools()` | List registered tools with OpenAI-compatible schemas |
| `run(messages, model, instructions, temperature, extra_create_args)` | Run a complete evaluated interaction |
| `run_stream(messages, model, instructions, temperature, extra_create_args)` | Run with streaming events |
| `run_with_approval(messages, model, ..., on_approval_required)` | Run with human-in-the-loop approval |
| `close()` | Close the underlying BIGHUB client |

---

## Links

- [bighub.io](https://bighub.io)
- [GitHub — bighub-io/bighub](https://github.com/bighub-io/bighub)
- [PyPI — bighub-openai](https://pypi.org/project/bighub-openai/)
- [PyPI — bighub](https://pypi.org/project/bighub/)

---

## License

MIT
