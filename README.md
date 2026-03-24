# BIGHUB

> Decision learning for AI agents.

BIGHUB is a decision layer that evaluates agent actions, returns structured recommendations, and learns from real outcomes over time.

```text
Agent proposes action
        ↓
BIGHUB evaluates in context
        ↓
returns recommendation + confidence + rationale
        ↓
agent / runtime decides what to do
        ↓
real outcome is reported
        ↓
future recommendations improve over time
```

---

## Packages

| Package | Language | Install | Description |
|---|---|---|---|
| **[bighub](sdk/python/)** | Python | `pip install bighub` | Core SDK — evaluate actions, receive recommendations, report outcomes, retrieve learned signals. |
| **[bighub-openai](adapters/python/openai/)** | Python | `pip install bighub-openai` | OpenAI Responses API adapter — evaluate tool calls, surface recommendations, learn from outcomes. |
| **[@bighub/bighub-mcp](servers/mcp/)** | TypeScript | `npm install @bighub/bighub-mcp` | MCP server — evaluate agent actions from any MCP client. |
| bighub-anthropic | Python | — | Anthropic adapter — *coming soon*. |
| bighub-openai (JS) | TypeScript | — | OpenAI adapter for Node.js — *coming soon*. |

---

## How it works

| Static guardrails | BIGHUB |
|---|---|
| Fixed allow / block logic | Structured recommendation in context |
| Rules only | Constraints + precedents + calibration + outcomes |
| One-off judgment | Trajectory- and history-aware evaluation |
| Prediction only | Prediction compared with real outcomes |
| Static thresholds | Recommendation quality improves over time |

---

## Quickstart (Python SDK)

```bash
pip install bighub
```

```python
import os
from bighub import BighubClient

client = BighubClient(api_key=os.getenv("BIGHUB_API_KEY"))

# 1. Submit an action for evaluation
result = client.actions.submit(
    action="update_price",
    value=150.0,
    domain="pricing",
    actor="AI_AGENT_001",
)

# 2. Inspect the recommendation
print(result["recommendation"])             # proceed, proceed_with_caution, review_recommended, do_not_proceed
print(result["recommendation_confidence"])   # high, medium, low
print(result["risk_score"])                  # 0.0 – 1.0

# 3. Act based on the recommendation
if result["recommendation"] in ("proceed", "proceed_with_caution"):
    execute_action()

    # 4. Report the real outcome
    client.outcomes.report(
        request_id=result["request_id"],
        status="SUCCESS",
        description="Price updated, no negative impact observed",
    )
elif result["recommendation"] == "review_recommended":
    request_human_review()

client.close()
```

Core loop: **evaluate → recommend → act → report outcome → learn**.

### Structured recommendation

BIGHUB primarily returns:

- `recommendation` — what to do (`proceed`, `proceed_with_caution`, `review_recommended`, `do_not_proceed`)
- `recommendation_confidence` — how confident (`high`, `medium`, `low`)
- `risk_score` — aggregated risk (0–1)
- `enforcement_mode` — how the recommendation is applied (`advisory`, `review`, `enforced`)
- `decision_intelligence` — rationale, evidence status, trajectory health, alternatives

Legacy fields such as `allowed`, `result`, and `reason` may still appear for backward compatibility, but they are not the primary product surface.

---

## Trajectory-aware evaluation

BIGHUB evaluates actions not only in isolation, but also in the context of what happened before. As outcomes accumulate, similar sequences and prior decisions improve future recommendations.

For costly and multi-step workflows, trajectory-aware signals mean the same action may be judged differently depending on what happened earlier in the sequence.

---

## Free BETA

Current Free BETA limits:

- 3 agents
- 2,500 actions / month
- 30 days history
- 1 environment

---

## Repository layout

```text
├── sdk/
│   └── python/
├── adapters/
│   ├── python/
│   │   ├── openai/
│   │   └── anthropic/
│   └── js/
│       └── openai/
├── servers/
│   └── mcp/
└── examples/
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

[MIT](LICENSE)
