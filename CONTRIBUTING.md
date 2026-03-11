# Contributing to BIGHUB

Thank you for your interest in contributing to BIGHUB — decision intelligence for autonomous AI agents.

## Repository structure

- **sdk/** — Core SDK packages (e.g. Python `bighub`).
- **adapters/** — Provider adapters (OpenAI, Anthropic, etc.) for Python and JS.
- **servers/** — Standalone servers (e.g. MCP).
- **examples/** — Sample code for Python and JavaScript/TypeScript.

## How to contribute

1. **Open an issue** to discuss bugs or features before large changes.
2. **Fork the repo** and create a branch from `main`.
3. **Follow existing style** and add tests where relevant.
4. **Submit a pull request** with a clear description of the change.

## Per-package guidelines

- **Python:** Use the existing `pyproject.toml` / `hatch` setup; run tests with `pytest`.
- **JS/TS:** Use the existing tooling in each package (e.g. `npm run test`).
- **MCP server:** See [servers/mcp/](servers/mcp/) for specific instructions.

## Code of conduct

Be respectful and constructive. We aim to keep the community inclusive and focused on building smarter decision intelligence for AI agents.
