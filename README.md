# BIGHUB

> Decision learning for AI agent actions.

This repository contains the open-source SDKs, adapters, and servers for BIGHUB.

BIGHUB evaluates agent actions, links them to real outcomes, and uses similar past cases to improve future decisions.

```text
LLM / Agent Runtime
        ↓
Provider Adapter or SDK
        ↓
BIGHUB API
        ↓
Evaluate → Decide
        ↓
execute / block / require approval
        ↓
report outcome
        ↓
learn from similar cases over time
```

---

## Packages

| Package | Language | Install | Description |
|---|---|---|---|
| **[bighub](sdk/python/)** | Python | `pip install bighub` | Core SDK — evaluate actions, report outcomes, and retrieve learned signals. |
| **[bighub-openai](adapters/python/openai/)** | Python | `pip install bighub-openai` | OpenAI Responses API adapter — evaluate tool calls and learn from outcomes. |
| **[@bighub/bighub-mcp](servers/mcp/)** | TypeScript | `npm install @bighub/bighub-mcp` | MCP server — evaluate agent actions from any MCP client. |
| bighub-anthropic | Python | — | Anthropic adapter — *coming soon*. |
| bighub-openai (JS) | TypeScript | — | OpenAI adapter for Node.js — *coming soon*. |

---

## How it works

| Rule-only systems | BIGHUB |
|---|---|
| Allow or block | Evaluate in context and learn from outcomes |
| Rules only | Rules plus precedents and calibration |
| One-off decisions | Similar past cases inform future ones |
| Prediction only | Prediction compared with reality |
| Fixed thresholds | Decision quality improves over time |

---

## Quickstart (Python SDK)

```bash
pip install bighub
```

```python
import os
from bighub import BighubClient

client = BighubClient(api_key=os.getenv("BIGHUB_API_KEY"))

result = client.actions.submit(
    action="update_price",
    value=150.0,
    domain="pricing",
    actor="AI_AGENT_001",
)

print(result["allowed"], result["reason"])

if result["allowed"]:
    execute_action()
    client.outcomes.report(
        request_id=result["request_id"],
        status="SUCCESS",
        description="Price updated, no negative impact observed",
    )

client.close()
```

Core loop: **evaluate → execute → report outcome → learn**.

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
