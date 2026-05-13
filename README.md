# BIGHUB

Better decisions for IT agent actions.

BIGHUB turns proposed IT agent actions into better decisions before they run. It builds a **Decision Packet**, runs **DecisionBrain**, and surfaces an execution outcome: proceed when appropriate (**`can_run`**), pause for human **review**, ask for more **context**, or advise **not to run**—with an optional **`better_action`** before execution only when BIGHUB actually produced one.

---

## What BIGHUB does

For each proposed IT action (access changes, deployments, rotations, IAM updates, incidents, integrations), BIGHUB:

- Normalizes intent and context into a **Decision Packet**
- Reasons with **DecisionBrain** (risk, confidence, precedent signals when present)
- Returns **`better_action`** when the backend proposes a distinct alternative—not a cosmetic rephrase of the original
- Maps the platform’s **`execution_mode`** (and legacy signals) into clear flags: **`can_run`**, **`needs_review`**, **`needs_more_context`**, **`should_not_run`**
- Supports optional **reviews** (`decision.request_review()`, SDK/MCP approvals) and optional **system context** helpers where implemented

---

## Quickstart (Python SDK)

```bash
pip install bighub
```

```python
from bighub import Bighub

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
    # Plug in your executor (Okta Admin API, runbook, CI gate, …)
    run(action_to_run)

bighub.close()
```

The recommended public flow:

**proposed IT action → Decision Packet → DecisionBrain → (`better_action` when real) → execution_mode / flags → review or context when needed**

---

## What a `Decision` returns

High-level fields developers use most often:

| Field / idea | Meaning |
|---|---|
| **`proposed_action`** | What your agent originally proposed |
| **`better_action`** | Distinct backend alternative when present; **`None`** if no real alternative was produced *(never trusted as “better” simply because it echoes the proposal)* |
| **`packet`** | **Decision Packet**: intent, system, constraints, candidates, risks, verification, etc., when returned |
| **`brain`** | **DecisionBrain**: reasoning summary, confidence, regret, review hints, etc., when returned |
| **`mode`** | SDK execution mode mapped from **`execution_mode`** and legacy payloads (for example **`review`**, **`needs_context`**, **`blocked`**) |
| **`can_run`**, **`needs_review`**, **`needs_more_context`**, **`should_not_run`** | Operational guidance before you execute |
| **`selected_model`** / **`model_selection`** | Routing when the backend actually selected a model or path—otherwise **`None`** / empty-ish structure (SDK does not invent routing) |

For full detail and `/actions/evaluate` field mapping, see [`sdk/python/README.md`](sdk/python/README.md).

---

## Benchmark proof

BIGHUB’s public SDK is centered on `bighub.decide(...)` and **Decision Packet** because the packet is the primitive that improves decision quality before execution.

On the April 2026 GPT-5.5 benchmark suite, BIGHUB improved average good decision rate from **41.11% to 73.14%** across **21 cells**, **2,520 labeled traces**, and **5,040 LLM calls**.

Same GPT-5.5 model, same frozen traces, same benchmark rubric. The baseline and packet arms differ only by whether the BIGHUB Decision Packet is included in the model input.

| View | Baseline GPT-5.5 | With BIGHUB | Uplift |
|---|---:|---:|---:|
| IT incident | 71.95% | 91.67% | +19.72 pp |
| IT helpdesk | 40.28% | 82.78% | +42.50 pp |
| Incident coldstart | 71.39% | 85.56% | +14.17 pp |
| Incident large | 44.17% | 86.67% | +42.50 pp |
| Incident large coldstart | 44.45% | 75.55% | +31.11 pp |
| Refunds | 11.95% | 47.50% | +35.55 pp |
| Refunds large | 3.61% | 42.22% | +38.61 pp |

Good decision rate measures match to the benchmark-defined optimal action.

These benchmarks measure decision quality under a frozen authored benchmark contract. They do not claim guaranteed production business lift. The packet and rubric share the same benchmark ontology by design, which makes the decision surfaces auditable, but also means this is a framework-aligned evaluation rather than unconstrained production ground truth.

Why this matters for the SDK:

- **`bighub.decide(...)`** is the ergonomic entrypoint for that packet-centered evaluation path.
- **DecisionBrain** interprets signals in the richer **Better Decision** response when the backend supplies them.
- **`better_action`** is only present when the service returns a genuinely distinct recommendation—not on every trace, and not by simple paraphrase of **`proposed_action`**.
- **Model routing** (**`selected_model`** / **`model_selection`**) appears when the backend actually performed selection; callers should tolerate **`None`** today.

---

## Packages

| Package | Language | Install | Description |
|---|---|---|---|
| **[bighub](sdk/python/)** | Python | `pip install bighub` | Core **Better Decision** SDK — `bighub.decide(...)`, Decision Packet / DecisionBrain helpers, reviews, optional outcomes. |
| **[bighub-openai](adapters/python/openai/)** | Python | `pip install bighub-openai` | OpenAI adapter — **Better Decision** layer on tool calls with `@agent.action` metadata. |
| **[@bighub/bighub-mcp](servers/mcp/)** | TypeScript | `npm install @bighub/bighub-mcp` | MCP server — **`bighub_decide`** and related tools for any MCP client. |
| **bighub-anthropic** | Python | — | Anthropic adapter — *coming soon* ([readme](adapters/python/anthropic/README.md)). |
| **bighub-openai (JS)** | TypeScript | — | OpenAI adapter for Node.js — *coming soon* ([readme](adapters/js/openai/README.md)). |

JavaScript-heavy workflows today: prefer the **[MCP server](servers/mcp/)** alongside your runtime.

---

## Optional: outcome reporting

When you choose to wire a learning loop later, report what happened **after** execution so future decisions improve:

```python
decision.report_outcome(
    status="completed",
    evidence={"deployment_id": "dep_123"},
)
```

Outcome reporting is **not** required for a first integration. The quickstart stays focused on the decision before execution.

---

## Legacy / low-level compatibility

Existing code can keep using **`BighubClient`**, **`AsyncBighubClient`**, and **`client.actions.evaluate(...)`** (evaluate payload / raw JSON paths). Older **`actions.submit`** flows remain documented in package-specific READMEs where relevant.

Prefer **`from bighub import Bighub`** + **`bighub.decide(...)`** for new IT agent integrations.

---

## Current limits / honest behavior

- **`better_action`** is **`None`** unless BIGHUB returned a distinct recommended alternative—not a wording-only duplicate of **`proposed_action`**.
- **`selected_model`** and **`model_selection`** fields reflect real backend routing when present; otherwise **`None`** (SDK does not fabricate routing).
- **Outcomes** are optional—you can ship **`decide` → execute/review/context** without calling **`report_outcome`**.
- Responses may include legacy fields (**`allowed`**, **`recommendation`**, **`risk_score`**, **`result`**) for dashboard and older clients; the modern surface is **`can_run`** / **`needs_review`** / **`execution_mode`** and friends.
- Free BETA product limits still apply—see **`sdk/python/README.md`**.

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
