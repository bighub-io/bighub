# BIGHUB Python examples

Sample patterns for **`bighub.decide(...)`**: proposed IT agent action → **Decision Packet** → **DecisionBrain** → flags and optional **`better_action`** before execution.

These examples use `bighub.decide(...)`, the same Decision Packet-centered flow used in BIGHUB’s GPT-5.5 benchmark suite.

---

## Quick example: privileged access review

```python
from bighub import Bighub


def run(action_to_run):
    """Execute via your toolchain (Okta Admin API, runbook, ticket workflow, …)."""
    raise NotImplementedError("Integrate with your executor.")


bighub = Bighub(api_key="...")

decision = bighub.decide(
    action="Grant temporary Okta admin access to users 1-9 for 48h",
    context={
        "system": "okta",
        "environment": "production",
        "ticket": "INC-8821",
    },
)

if decision.needs_review:
    decision.request_review()
elif decision.needs_more_context:
    print("More context required:", decision.reason)
elif decision.should_not_run:
    print("Do not run:", decision.reason)
elif decision.can_run:
    action_to_run = decision.better_action or decision.proposed_action
    run(action_to_run)

bighub.close()
```

- **`better_action`** may be **`None`**: use **`decision.better_action or decision.proposed_action`** only after **`can_run`** and the review/context/do-not-run branches above. BIGHUB does not treat a paraphrase of the same action as a “better” alternative.
- **`selected_model`** / **`model_selection`** may be **`None`** unless the backend actually selected a path.

---

## More IT-oriented `decide` calls

Rotate credentials across production tiers:

```python
decision = bighub.decide(
    action="Rotate production database credentials for billing and payments shards",
    context={
        "system": "database",
        "environment": "production",
        "services": ["billing", "payments"],
        "ticket": "CHG-4401",
    },
)
```

Deploy with explicit rollback posture:

```python
decision = bighub.decide(
    action="Roll out billing-api v3.12 to prod and scale replicas to 8",
    context={
        "system": "kubernetes",
        "environment": "production",
        "service": "billing-api",
        "version": "v3.12",
    },
)
```

Incident channel update:

```python
decision = bighub.decide(
    action="Post all-clear to #incidents for INC-9912 after verifier passes",
    context={
        "system": "slack",
        "environment": "production",
        "channel": "#incidents",
        "ticket": "INC-9912",
    },
)
```

Reuse the same **review / context / should_not_run / can_run + better_action-or-proposed** branching as in the first example.

---

## OpenAI tool runtime

Use **`bighub-openai`** to attach the Better Decision layer to OpenAI Responses tool calls (`BighubOpenAI`, `@agent.action`). See **[adapters/python/openai/README.md](../../adapters/python/openai/)**.

---

## Legacy / low-level API

Older snippets may use **`BighubClient`** with **`actions.submit`** or **`actions.evaluate`** returning raw payloads. Prefer **`bighub.decide`** for IT workflows; legacy calls remain supported for backward compatibility.

```python
from bighub import BighubClient

client = BighubClient(api_key="...")

legacy = client.actions.evaluate(
    action="example_action",
    value=150.0,
    domain="example_domain",
    actor="agent_001",
)
# Or use client.actions.submit(...) as an alias of evaluate(...)

# Raw dict surfaces (recommendation, risk_score, etc.) still supported

client.close()
```

---

## References

Free BETA limits and finer-grained APIs: **[sdk/python/README.md](../../sdk/python/)** · MCP: **[servers/mcp/README.md](../../servers/mcp/)**
