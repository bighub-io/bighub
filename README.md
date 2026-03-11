# BIGHUB

> Self-improving rules for AI agents.

Define your boundaries. BIGHUB simulates every action, learns from every decision, and makes your rules smarter over time.

Every agent action is stress-tested across 100+ scenarios and scored for risk, fragility, and blast radius — before execution. Patterns are detected, policies improve automatically, and your agents get smarter over time.

```text
LLM / Agent Runtime
        ↓
Provider Adapter (e.g. bighub-openai)
        ↓
BIGHUB Decision Intelligence API
        ↓
Simulate → Score → Enforce → Learn
        ↓
execute / block / require approval
```

---

## Packages

| Package | Language | Install | Description |
|---------|----------|---------|-------------|
| **[bighub](sdk/python/)** | Python | `pip install bighub` | Core SDK — actions, rules, approvals, kill switch, webhooks, API keys, Future Memory. |
| **[bighub-openai](adapters/python/openai/)** | Python | `pip install bighub-openai` | OpenAI Responses API adapter — simulate and score tool/function calls with decision intelligence. |
| **[@bighub/bighub-mcp](servers/mcp/)** | TypeScript | `npm install @bighub/bighub-mcp` | MCP server — use BIGHUB decision intelligence from any Model Context Protocol client. |
| bighub-anthropic | Python | — | Anthropic adapter — *coming soon*. |
| bighub-openai (JS) | TypeScript | — | OpenAI adapter for Node.js — *coming soon*. |

---

## Why BIGHUB?

| Guardrails | BIGHUB |
|---|---|
| Block or allow | Simulate, score, enforce, and learn |
| Static rules | Rules that improve from every decision |
| No visibility into risk | Fragility, blast radius, and impact scored before execution |
| Same policy forever | Future Memory detects patterns and recommends smarter policies |
| One agent, one config | Scale across domains and agents with compounding intelligence |

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
    domain="financial_actions",
    actor="AI_AGENT_001",
)

print(result["allowed"], result["risk_score"])
print(result["simulation"]["fragility_score"])
client.close()
```

Every call returns a decision with risk scoring and simulation results — even on the free plan (100 scenarios).

---

## Repository layout

```
├── sdk/
│   └── python/            ← pip install bighub
├── adapters/
│   ├── python/
│   │   ├── openai/        ← pip install bighub-openai
│   │   └── anthropic/     ← coming soon
│   └── js/
│       └── openai/        ← coming soon
├── servers/
│   └── mcp/               ← npm install @bighub/bighub-mcp
└── examples/
    ├── python/
    └── js/
```

---

## Links

- [bighub.io](https://bighub.io)
- [GitHub — bighub-io/bighub](https://github.com/bighub-io/bighub)
- [PyPI — bighub](https://pypi.org/project/bighub/)
- [PyPI — bighub-openai](https://pypi.org/project/bighub-openai/)
- [npm — @bighub/bighub-mcp](https://www.npmjs.com/package/@bighub/bighub-mcp)

## License

[MIT](LICENSE)
