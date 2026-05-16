# bighub-openai

Better decisions for OpenAI tool calls.

> Beta release: this is the first public Better Decision OpenAI adapter beta.

**`bighub-openai` adds BIGHUB's Better Decision layer to OpenAI agents before they execute risky IT tool calls, turning proposed IT actions into better decisions before execution.**

```text
OpenAI Responses API  ->  bighub-openai          ->  BIGHUB
tool call             ->  proposed IT action     ->  Decision Packet + DecisionBrain
runtime               ->  decision signals       ->  execution mode or review
outcome later         ->  optional report        ->  future decisions improve
```

Use it when your OpenAI agent can take actions such as:

- granting Okta or IAM access
- triggering CI/CD deploys
- running Terraform, Kubernetes, or Argo CD actions
- rotating credentials
- posting incident updates
- continuing after Trivy, Syft, or SBOM security checks
- calling internal APIs that change production state

```bash
pip install --pre bighub-openai
```

For future stable releases, use:

```bash
pip install bighub-openai
```

Requires Python 3.9+.

Dependencies:

- `bighub>=0.1.0b5,<0.2.0`
- `openai>=2.0.0,<3.0.0`

---

## Quickstart

```python
import os
from bighub_openai import BighubOpenAI


agent = BighubOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    bighub_api_key=os.getenv("BIGHUB_API_KEY"),
    actor="ops-agent",
    domain="it_actions",
)


@agent.action(system="okta", risk="high", environment="production")
def grant_access(user_id: str, group: str, duration: str) -> dict:
    return {"ok": True, "user_id": user_id, "group": group, "duration": duration}


response = agent.run(
    messages=[{"role": "user", "content": "Grant Alice temporary Okta admin access for 48h"}],
    model="gpt-5.5",
)

last = response["execution"]["last"]
print(last["status"])                   # executed, blocked, approval_required, tool_error
print(last["decision"].get("mode"))    # review, autonomous, constrained, blocked, needs_context
print(last["decision"].get("risk"))
print(last["decision"].get("reason"))

decision = last["decision"]
print(decision.get("salient_factors"))
print(decision.get("responsible_action_space"))
```

`agent.action(...)` auto-generates a strict JSON schema from the Python function signature and attaches system context. `GuardedOpenAI` remains available as a compatibility alias.

---

## When to use `bighub-openai`

Use this adapter when your OpenAI-based agent makes tool calls that:

- change infrastructure or production state
- may require review depending on system, scope, environment, or timing
- benefit from decision-time and polled operational context
- should stop, pause for review, or ask for more context before risky execution

If your agent only reads data or produces text, you probably do not need this adapter.

---

## How it works

For every tool call, the adapter follows the same loop:

1. The model proposes a tool call.
2. The adapter captures action, arguments, actor, domain, and system metadata.
3. BIGHUB evaluates the action and may return a **Decision Packet**, **DecisionBrain** signals, and execution guidance.
4. The adapter resolves the execution result: execute, block, or require approval.
5. If enabled, optional outcome reporting and memory ingestion happen after execution.

Recommended mental model:

**OpenAI tool call -> proposed IT action -> Decision Packet -> DecisionBrain -> execution mode / review -> optional outcome reporting**

---

## Response Shape

Representative shape from `run()`:

```python
{
  "llm_response": {...},
  "execution": {
    "events": [...],
    "last": {
      "tool": "grant_access",
      "status": "approval_required",
      "decision": {
        "request_id": "req_abc123",
        "better_action": "Grant scoped Okta admin access for 2h instead of 48h",
        "mode": "review",
        "can_run": False,
        "needs_review": True,
        "needs_more_context": False,
        "should_not_run": False,
        "risk": 0.78,
        "reason": "Production admin access for 48h is broader than necessary.",
        "responsible_action_space": {
          "available": [],
          "constrained": [],
          "forbidden": [],
          "information_gathering": []
        },
        "salient_factors": [
          {
            "factor": "high_blast_radius",
            "severity": "warning",
            "reason": "Production admin access has broad impact."
          }
        ],
        "operational_intent": {
          "declared": "Grant Alice temporary Okta admin access for 48h",
          "inferred": "Grant the minimum necessary access in production",
          "confidence": 0.72,
          "mismatch": true
        },
        "agent_operational_body": {
          "can_touch": ["okta"],
          "can_verify": ["verify access grant"],
          "can_rollback": [],
          "cannot_observe": [],
          "requires_human": ["human_review"]
        },
        "action_interpretation_layer": {
          "raw_action": "Grant Alice admin for 48h",
          "interpreted_action": "temporary privilege escalation in production identity system",
          "action_family": "privilege_escalation"
        },
        "decision_packet": {...},
        "decision_brain": {...}
      },
      "recommendation": "review_recommended",
      "risk_score": 0.78,
      "enforcement_mode": "review"
    }
  }
}
```

The adapter returns the full raw BIGHUB decision under `last["decision"]`. When the backend returns the newer Better Decision fields, those remain the preferred application surface.

### Primary decision signals

| Field | Description |
|---|---|
| `better_action` | A real backend-produced alternative when available; otherwise `None` |
| `mode` | Execution mode such as `autonomous`, `constrained`, `review`, `blocked`, or `needs_context` |
| `can_run` | Whether the tool call can execute now |
| `needs_review` | Whether a human review should happen first |
| `needs_more_context` | Whether the agent should collect more information |
| `should_not_run` | Whether BIGHUB recommends not executing |
| `risk` | Top-level risk score when provided |
| `reason` | Human-readable reason when provided |
| `responsible_action_space` | Responsible action options grouped as `available`, `constrained`, `forbidden`, and `information_gathering` when returned by BIGHUB |
| `salient_factors` | Decision-time factors BIGHUB identified as important for this tool call, such as high blast radius, weak verifier coverage, unavailable rollback, active incident, or open obligations |
| `operational_intent` | Declared and inferred operational intent for the proposed tool call |
| `agent_operational_body` | What the agent can touch, verify, rollback, cannot observe, or must escalate |
| `action_interpretation_layer` | Interpreted operational meaning of the raw tool call |
| `decision_packet` | Structured context used for the decision |
| `decision_brain` | DecisionBrain reasoning summary and related signals |

`responsible_action_space`, `salient_factors`, `operational_intent`, `agent_operational_body`, and `action_interpretation_layer` are explanatory decision signals. They do not override runtime gating. Execution is still controlled by `mode`, `can_run`, `needs_review`, `should_not_run`, `recommendation`, `allowed`, and `requires_approval`.

### Semantic decision views

When available, BIGHUB also returns semantic views of the proposed action:

- `operational_intent`: declared and inferred operational intent
- `agent_operational_body`: what the agent can touch, verify, rollback, or cannot observe
- `action_interpretation_layer`: interpreted operational meaning of the raw action

These fields are explanatory and additive. Execution remains controlled by `mode`, `can_run`, `needs_review`, `should_not_run`, and related gating fields.

### Execution statuses

| Status | Description |
|---|---|
| `executed` | Tool ran successfully |
| `blocked` | Runtime prevented execution |
| `approval_required` | Waiting for human approval |
| `tool_error` | Tool raised an exception during execution |

### Compatibility signals

For backward compatibility, `last` may also expose convenience fields such as `recommendation`, `risk_score`, `enforcement_mode`, and legacy decision payload keys like `allowed`, `result`, or `reason`. Prefer the structured fields inside `last["decision"]` when they are present.

---

## Configuration

```python
agent = BighubOpenAI(
    bighub_api_key="bh_live_xxx",
    openai_api_key="sk-xxx",
    actor="ops-agent",
    domain="it_actions",
    decision_mode="submit",      # or "submit_payload"
    fail_mode="closed",          # fail safe on BIGHUB errors
    max_tool_rounds=8,
    model_selection="auto",
    provider_timeout_seconds=30.0,
    provider_max_retries=2,
    outcome_reporting=True,
    memory_enabled=True,
)
```

Key parameters:

- `decision_mode`: `submit` or `submit_payload`
- `fail_mode`: `closed` or `open`
- `outcome_reporting`: optional automatic reporting after execution
- `memory_enabled`: optional ingestion of tool-call decision events
- `model_selection`: routing hint forwarded to BIGHUB context

---

## Registering tools

Basic registration:

```python
agent.tool("deploy_service", deploy_service)
```

With metadata extracted from arguments:

```python
agent.tool(
    "sync_argocd_app",
    sync_argocd_app,
    domain="it_actions",
    actor="ops-agent",
    action_name="argocd_sync",
    metadata_from_args=lambda a: {
        "system": "argocd",
        "environment": a.get("environment"),
        "app": a.get("app"),
    },
)
```

Other common patterns:

- `value_from_args` for cost-like signals
- `target_from_args` for resource targeting
- `parameters_schema` for custom JSON schema
- `register_tool(...)` for the full lower-level API

---

## Streaming

```python
for event in agent.run_stream(
    messages=[{"role": "user", "content": "Sync checkout-service in Argo CD production"}],
    model="gpt-5.5",
):
    if event["type"] == "execution_event":
        print(event["event"]["tool"], event["event"]["status"])
```

`run_stream()` emits incremental model output and execution events, then finishes with the same final response shape as `run()`.

---

## Async

```python
from bighub_openai import AsyncBighubOpenAI


async with AsyncBighubOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    bighub_api_key=os.getenv("BIGHUB_API_KEY"),
    actor="ops-agent",
    domain="it_actions",
) as agent:
    agent.tool("rotate_credentials", rotate_credentials)
    response = await agent.run(
        messages=[{"role": "user", "content": "Rotate production database credentials"}],
        model="gpt-5.5",
    )
```

---

## Human-in-the-loop approvals

```python
result = agent.run_with_approval(
    messages=[{"role": "user", "content": "Grant temporary Okta admin access for 48h"}],
    model="gpt-5.5",
    on_approval_required=lambda ctx: {
        "resolution": "approved",
        "comment": "approved by on-call",
    },
)
```

When BIGHUB returns an approval-required decision, the adapter pauses execution and calls `on_approval_required` with the decision context.

---

## Optional outcome reporting

If `outcome_reporting=True`, the adapter can automatically report successful execution, blocked execution, and tool errors back to BIGHUB after the tool decision resolves.

This is optional. The primary wedge is still the Better Decision before execution.

---

## Optional decision memory

If `memory_enabled=True`, the adapter ingests structured events about tool calls, decisions, and outcomes into BIGHUB memory for future retrieval and pattern detection.

---

## Compatibility

The modern path is `BighubOpenAI` / `AsyncBighubOpenAI`.

Compatibility aliases remain available:

- `GuardedOpenAI` -> `BighubOpenAI`
- `AsyncGuardedOpenAI` -> `AsyncBighubOpenAI`

---

## API Reference

| Method | Description |
|---|---|
| `tool(name, fn, **kwargs)` | Register a tool |
| `register_tool(name, fn, ...)` | Register a tool with full options |
| `list_tools()` | List registered OpenAI-compatible tool schemas |
| `run(messages, model, ...)` | Run a complete evaluated interaction |
| `run_stream(messages, model, ...)` | Run with streaming events |
| `run_with_approval(messages, model, ..., on_approval_required)` | Run with approval callback support |
| `close()` | Close the underlying BIGHUB client |

---

## Links

- [bighub.io](https://bighub.io)
- [GitHub repository](https://github.com/bighub-io/bighub)
- [PyPI - bighub-openai](https://pypi.org/project/bighub-openai/)
- [PyPI - bighub](https://pypi.org/project/bighub/)
- [MCP server](https://www.npmjs.com/package/@bighub/bighub-mcp)

---

## License

Apache-2.0
