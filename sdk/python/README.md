# BIGHUB SDK

Better decisions for IT agent actions.

> Beta release: this is the first public Better Decision SDK beta.

**BIGHUB helps AI agents and CI/CD workflows make better IT decisions before execution.**

It takes a proposed IT action, builds a **Decision Packet**, runs **DecisionBrain**, and returns execution guidance:

- proceed when appropriate
- pause for review
- ask for more context
- advise not to run
- suggest a real `better_action` only when the backend actually produced one

```bash
pip install --pre bighub
```

For future stable releases, use:

```bash
pip install bighub
```

Python 3.9+. Single dependency: `httpx`.

---

## Quick Start

```python
from bighub import Bighub


def run(action_to_run):
    raise NotImplementedError("Connect this to your executor.")


bighub = Bighub(api_key="your_api_key")

decision = bighub.decide(
    action="Roll out billing-api v3.12 to production",
    context={
        "system": "kubernetes",
        "environment": "production",
        "service": "billing-api",
        "ticket": "CHG-4401",
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

for factor in decision.salient_factors:
    print("Important factor:", factor.get("factor"), factor.get("severity"))

space = decision.responsible_action_space or {}
print("Available actions:", space.get("available", []))
print("Constrained actions:", space.get("constrained", []))

bighub.close()
```

Recommended flow:

**proposed IT action -> Decision Packet -> DecisionBrain -> `better_action` when real -> execution mode and flags -> review or context when needed**

---

## When to use BIGHUB

Use BIGHUB before risky actions such as:

- GitHub Actions, GitLab CI, or Jenkins deploys
- `terraform apply`
- Argo CD sync or Kubernetes / OpenShift rollout
- Okta or IAM access changes
- credential rotation
- incident updates in Slack
- security gates after Trivy / Syft / SBOM signals
- production actions that may need review or additional context

If your workflow only reads data or performs harmless lookups, you probably do not need BIGHUB.

---

## What a `Decision` returns

High-value fields most workflows care about:

- `better_action`: a real backend-produced alternative when available, otherwise `None`
- `mode`: execution guidance such as `autonomous`, `constrained`, `review`, `blocked`, or `needs_context`
- `can_run`, `needs_review`, `needs_more_context`, `should_not_run`: direct operational flags
- `risk`: top-level risk score when provided
- `decision_path`: routing or evaluation path when provided
- `packet`: the `DecisionPacket` used for the decision
- `brain`: the `DecisionBrainResult` with reasoning summary, confidence, expected regret when provided, and related signals
- `selected_model`: present only when the backend actually selected one
- `responsible_action_space`: the responsible action space for the current situation, grouped into `available`, `constrained`, `forbidden`, and `information_gathering` actions
- `salient_factors`: the most important decision-time factors BIGHUB identified, such as weak verifier coverage, unavailable rollback, open obligations, active incidents, irreversibility, or high blast radius
- `operational_intent`: declared and inferred operational intent for the proposed action
- `agent_operational_body`: what the agent can touch, verify, rollback, cannot observe, or must escalate
- `action_interpretation_layer`: the interpreted operational meaning of the raw action

For a smaller stable surface, use `decision.brief()`:

```python
brief = decision.brief()

print(brief.salient_factors)
print(brief.action_space_counts)
print(brief.action_family)
print(brief.intent_mismatch)

if brief.can_run:
    run(brief.recommended_action)
elif brief.needs_review:
    print("Review required:", brief.reason)
```

`decision.brief()` keeps this compact: it exposes salient factor names and action-space counts, while the full `Decision` object keeps the detailed `responsible_action_space` and `salient_factors` payloads.

### Semantic decision views

When available, BIGHUB also returns semantic views of the proposed action:

- `operational_intent`: declared and inferred operational intent
- `agent_operational_body`: what the agent can touch, verify, rollback, or cannot observe
- `action_interpretation_layer`: interpreted operational meaning of the raw action

These fields are explanatory and additive. Execution remains controlled by `mode`, `can_run`, `needs_review`, `should_not_run`, and related gating fields.

---

## Honest behavior

The SDK is intentionally strict about what it does and does not invent:

- `better_action` is `None` unless BIGHUB returned a genuinely distinct recommendation
- `selected_model` is `None` unless the backend actually selected one
- `decision_path` and model-selection fields stay empty when the backend did not provide them
- outcomes are optional and not required for a first integration
- legacy `BighubClient` and `client.actions.evaluate(...)` remain available for existing integrations

If a backend `decision_packet` has no `packet_sha256`, the SDK computes a stable local hash and marks it with `packet.packet_sha256_is_local=True`.

---

## Optional: outcome reporting

If you want a learning loop later, report what happened after execution:

```python
decision.report_outcome(
    status="completed",
    evidence={"deployment_id": "dep_123"},
)
```

Outcome reporting is optional. The primary integration wedge is still the decision before execution.

After outcomes are reported, you can inspect learning impact:

```python
from bighub import BighubClient


client = BighubClient(api_key="your_api_key")

impact = client.learning.impact()
print(impact.get("future_decisions_verdict_changed"))
print(impact.get("avg_regret_reduction"))

metrics = client.learning.disagreement_metrics()
print(metrics.get("avg_regret_reduction"))

client.close()
```

---

## Learning impact

BIGHUB can also expose post-outcome learning metrics when outcomes and disagreements are available.

```python
from bighub import BighubClient


client = BighubClient(api_key="your_api_key")

impact = client.learning.impact()
print(impact.get("future_decisions_learning_influenced"))
print(impact.get("future_decisions_verdict_changed"))
print(impact.get("avg_regret_reduction"))

disagreements = client.learning.disagreement_metrics()
print(disagreements.get("bighub_regret_reduction_rate"))
print(disagreements.get("avg_regret_reduction"))

client.close()
```

These metrics are post-outcome signals. They are not required for first integration and are separate from the pre-execution decision returned by `bighub.decide(...)`.

---

## CI/CD and system integrations

You can connect system evidence so BIGHUB sees recent operational context before deciding.

For lower-level resources, `BighubClient` remains available:

```python
from bighub import BighubClient

client = BighubClient(api_key="your_api_key")

client.systems.save_connection(
    "gitlab",
    {
        "base_url": "https://gitlab.com",
        "gitlab_token": "glpat_...",
        "project_id": "123",
    },
    display_name="GitLab production",
)

client.systems.update_poll_schedule("gitlab", enabled=True, interval_seconds=300)
client.systems.poll("gitlab")
world = client.systems.world_state()

client.close()
```

System providers currently supported by the SDK/API include `okta`, `slack`, `github`, `datadog`, `sentry`, `aws_cloudtrail`, `terraform`, `kubernetes`, `argocd`, `gitlab`, `jenkins`, `azure`, `prometheus`, `grafana`, and `openshift`.

Poll snapshots and histories are redacted before persistence and exposure. They provide best-effort operational context; they are not a replacement for production monitoring.

Typical uses:

- gate a GitHub Actions or GitLab deploy with recent operational context
- inspect Kubernetes, Argo CD, Prometheus, or Grafana state before rollout
- apply IAM or Okta changes with better review posture
- incorporate security and incident signals before execution

---

## Compatibility

The modern entrypoint is `bighub.decide(...)`.

For existing integrations, legacy `BighubClient`, `client.actions.submit(...)`, and `client.actions.evaluate(...)` remain supported.

---

## Links

- [bighub.io](https://bighub.io)
- [GitHub repository](https://github.com/bighub-io/bighub)
- [Python examples](https://github.com/bighub-io/bighub/tree/main/examples/python)
- [OpenAI adapter](https://github.com/bighub-io/bighub/tree/main/adapters/python/openai)
- [MCP server](https://github.com/bighub-io/bighub/tree/main/servers/mcp)
- [PyPI - bighub](https://pypi.org/project/bighub/)
- [PyPI - bighub-openai](https://pypi.org/project/bighub-openai/)

---

## License

Apache-2.0
