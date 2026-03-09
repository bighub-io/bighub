# BIGHUB Public

> Execution governance for autonomous AI agents.

BIGHUB sits between agent reasoning and real-world execution. Every action is validated against explicit policies before it runs.

## Packages overview

| Package | Install | Description |
|--------|--------|-------------|
| **bighub** | `pip install bighub` | Core Python SDK — actions, rules, approvals, API keys. |
| **bighub-openai** | `pip install bighub-openai` | OpenAI adapter — govern tool/function calls with BIGHUB. |
| **bighub-anthropic** | — | Anthropic adapter — *coming soon*. |
| **bighub-openai (JS)** | — | OpenAI adapter for Node.js — *coming soon*. |
| **bighub-mcp** | `npm install bighub-mcp` | MCP server — use BIGHUB from Model Context Protocol. |

## Repository layout

```
bighub-public/
├── README.md              ← this file
├── CONTRIBUTING.md
├── LICENSE
├── .gitignore
├── sdk/
│   └── python/            ← pip install bighub
├── adapters/
│   ├── python/
│   │   ├── openai/        ← pip install bighub-openai
│   │   └── anthropic/     ← coming soon
│   └── js/
│       └── openai/        ← coming soon
├── servers/
│   └── mcp/               ← npm install bighub-mcp
└── examples/
    ├── python/
    └── js/
```

## Quick links

- **Core SDK (Python):** [sdk/python/](sdk/python/) — [PyPI: bighub](https://pypi.org/project/bighub/)
- **OpenAI adapter (Python):** [adapters/python/openai/](adapters/python/openai/) — [PyPI: bighub-openai](https://pypi.org/project/bighub-openai/)
- **MCP server:** [servers/mcp/](servers/mcp/)
- **Examples:** [examples/](examples/)

## License

[MIT](LICENSE)
