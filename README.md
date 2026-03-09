# BIGHUB

> Control plane for AI agent actions.

Validate, bound, and govern every autonomous AI agent decision before it acts — making autonomy safe, intelligent, and ready for production.

BIGHUB sits between AI reasoning and real-world execution. Agents can plan and decide, but real-world actions execute only within your defined limits.

```text
LLM / Agent Runtime
        ↓
Provider Adapter (e.g. bighub-openai)
        ↓
BIGHUB Control Plane API
        ↓
Rules + Approvals + Memory + Policy Intelligence
        ↓
execute / block / require approval
```

---

## Packages

| Package | Language | Install | Description |
|---------|----------|---------|-------------|
| **[bighub](sdk/python/)** | Python | `pip install bighub` | Core SDK — actions, rules, approvals, kill switch, webhooks, API keys, Future Memory. |
| **[bighub-openai](adapters/python/openai/)** | Python | `pip install bighub-openai` | OpenAI Responses API adapter — govern tool/function calls with BIGHUB policies. |
| **[@bighub/bighub-mcp](servers/mcp/)** | TypeScript | `npm install @bighub/bighub-mcp` | MCP server — use BIGHUB governance from any Model Context Protocol client. |
| bighub-anthropic | Python | — | Anthropic adapter — *coming soon*. |
| bighub-openai (JS) | TypeScript | — | OpenAI adapter for Node.js — *coming soon*. |

---

## Why BIGHUB?

| Without BIGHUB | With BIGHUB |
|---|---|
| Agent acts directly in production | Every action validated before execution |
| Guardrails are suggestions | Policies are enforced at runtime |
| Logging shows what happened | Decisions are blocked *before* they happen |
| Autonomy grows, exposure grows | Bounded autonomy, controlled risk |

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
client.close()
```

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
