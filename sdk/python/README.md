# BIGHUB Python SDK

> Evaluate agent actions, receive structured recommendations, report real outcomes, and improve future decisions from experience.

The BIGHUB Python SDK connects your agents to a decision layer that learns over time.

Use it to:

- evaluate actions before they run and receive structured recommendations
- report what actually happened after execution
- retrieve similar past cases and learned signals
- compare prediction vs reality
- improve how future actions are judged

```bash
pip install bighub
```

Python 3.9+. Single dependency: `httpx`.

---

## Quick Start

```python
from bighub import BighubClient

client = BighubClient(api_key="your_api_key")

# 1. Submit a decision for evaluation
result = client.actions.submit(
    action="refund_full",
    value=450.0,
    domain="customer_transactions",
    target="order_12345",
    actor="refund_agent",
)

# 2. Inspect the recommendation
print(result["recommendation"])             # proceed, proceed_with_caution, review_recommended, do_not_proceed
print(result["recommendation_confidence"])   # high, medium, low
print(result["risk_score"])                  # 0.0 – 1.0

# 3. Let your agent or runtime act
if result["recommendation"] in ("proceed", "proceed_with_caution"):
    execute_refund()

    # 4. Report the real outcome
    client.outcomes.report(
        request_id=result["request_id"],
        status="SUCCESS",
        description="Refund processed, customer retained",
    )
elif result["recommendation"] == "review_recommended":
    request_human_review()
else:
    skip_refund()

client.close()
```

That is the core loop:

**submit for evaluation → inspect recommendation → act → report outcome → learn**

---

## Structured recommendation

BIGHUB primarily returns:

- `recommendation` — what to do (`proceed`, `proceed_with_caution`, `review_recommended`, `do_not_proceed`)
- `recommendation_confidence` — how confident (`high`, `medium`, `low`)
- `risk_score` — aggregated risk (0–1)
- `enforcement_mode` — how the recommendation is applied (`advisory`, `review`, `enforced`)
- `decision_intelligence` — rationale, evidence status, trajectory health, alternatives

Legacy fields such as `allowed`, `result`, and `reason` may still appear for backward compatibility, but they are not the primary product surface.

---

## What This SDK Is For

BIGHUB is useful when agent actions can create real operational consequences, for example:

- refunds
- pricing changes
- CRM updates
- workflow execution
- infrastructure actions
- internal operations with approval thresholds

Instead of treating each action like the first time, BIGHUB lets future actions benefit from:

- real outcomes
- similar past cases
- calibration between prediction and reality
- trajectory-aware evaluation across multi-step workflows
- learned advisories and risk patterns

---

## Core Loop

### 1) Submit a decision for evaluation

```python
result = client.actions.submit(
    action="increase_price",
    value=15.0,
    domain="customer_transactions",
    target="sku_789",
)

print(result["recommendation"])             # proceed_with_caution
print(result["recommendation_confidence"])   # medium
print(result["risk_score"])                  # 0.42
print(result["warnings"])                    # ["Similar actions caused margin drops"]
```

### 2) Inspect the recommendation and decision signals

```python
if result["recommendation"] in ("proceed", "proceed_with_caution"):
    apply_price_change()
elif result["recommendation"] == "review_recommended":
    request_human_review()
else:
    skip_action()
```

### 3) Report the real outcome

```python
client.outcomes.report(
    request_id=result["request_id"],
    status="CHURN",
    description="Conversion dropped 12% after price increase",
    revenue_impact=-3200.0,
)
```

### 4) Reuse what was learned on future decisions

```python
precedents = client.precedents.query(
    domain="customer_transactions",
    action="increase_price",
    risk_score=0.42,
)

print(precedents["total_precedents"])
print(precedents["outcomes"])
```

---

## Core Resources

### Core loop

| Resource | Purpose |
|---|---|
| `client.actions` | Submit actions for evaluation and receive recommendations |
| `client.outcomes` | Report and query real outcomes |
| `client.cases` | Create and manage DecisionCases |

### Learning signals

| Resource | Purpose |
|---|---|
| `client.precedents` | Retrieve similar past cases |
| `client.retrieval` | Aggregate multi-signal precedent retrieval |
| `client.calibration` | Compare prediction vs reality |
| `client.insights` | Retrieve learned advisories and risk patterns |
| `client.simulations` | Inspect simulation snapshots and accuracy |

### Operating layer

| Resource | Purpose |
|---|---|
| `client.constraints` | Configure explicit operating limits and intervention boundaries |
| `client.rules` | Backward-compatible alias for `client.constraints` |

---

## Trajectory-aware evaluation

BIGHUB evaluates actions not only in isolation, but also in the context of what happened before. As outcomes accumulate, similar sequences and prior decisions improve future recommendations.

For costly and multi-step workflows, trajectory-aware signals mean the same action may be judged differently depending on what happened earlier in the sequence.

---

## Decision Cases

A DecisionCase connects:

- the proposed action
- the context around it
- the recommendation made before execution
- the real outcome observed later

Create and manage a decision case directly:

```python
case = client.cases.create(
    domain="customer_transactions",
    action={"tool": "refund_full", "action": "refund_full", "value": 900.0},
    verdict={"verdict": "ALLOWED", "risk_score": 0.35, "confidence": 0.86},
    context={"axes": {"reversibility": 0.9}, "risk_score": 0.35},
    goal_summary="Customer requested refund for delayed order",
    trigger_source="support_ticket",
)

client.cases.report_outcome(
    case["case_id"],
    status="FRAUD",
    description="Fraudulent refund detected 3 days later",
    correction_needed=True,
    revenue_impact=-900.0,
)
```

The `verdict` field is the internal execution verdict. The primary external surface is the structured recommendation returned by `client.actions.submit(...)`.

Query cases with outcomes:

```python
cases = client.cases.list(
    domain="customer_transactions",
    has_outcome=True,
    min_risk_score=0.3,
    limit=20,
)
```

---

## Precedents And Learned Signals

Before or after a decision, you can inspect what BIGHUB has learned from similar past cases.

### Query precedents

```python
precedents = client.precedents.query(
    domain="customer_transactions",
    action="refund_full",
    risk_score=0.35,
)

print(precedents["total_precedents"])
print(precedents["outcomes"])
```

### Check calibration

```python
cal = client.calibration.report(domain="customer_transactions")
print(cal["calibration_quality"])
print(cal["bias_direction"])
```

### Retrieve advisories

```python
advice = client.insights.advise(
    tool="increase_price",
    action="increase_price",
    domain="customer_transactions",
)

print(advice["advisories"])
```

These signals help future actions get judged with more experience.

---

## Recommendation quality analytics

Track whether BIGHUB's recommendations lead to better outcomes:

```python
quality = client.outcomes.recommendation_quality(domain="customer_transactions")

print(quality["follow_rate"])                 # how often agents follow the recommendation
print(quality["positive_after_following"])     # success rate when followed
print(quality["quadrants"])                   # followed_positive, followed_negative, ignored_positive, ignored_negative
print(quality["trend"])                       # weekly time series
```

Get a self-contained partner view for one domain:

```python
view = client.outcomes.partner_view("customer_transactions")
# overview, recommendation_quality, trend, by_action, sparse_evidence, examples
```

---

## More Resources

Use these when you need deeper platform operations beyond the core loop above.

### Runtime ingestion

Use ingestion endpoints when you want to route structured runtime data into BIGHUB.

```python
client.ingest.event(
    event_type="ACTION_EXECUTED",
    request_id="req_abc123",
    domain="customer_transactions",
    action={"tool": "refund_full", "arguments": {"amount": 450}},
    execution={"executed": True, "status_code": 200},
)

client.ingest.reconcile(
    key_name="request_id",
    key_value="req_abc123",
    outcome={
        "event_type": "OUTCOME_OBSERVED",
        "outcome": {"status": "SUCCESS", "description": "Charge completed"},
    },
)

stats = client.ingest.stats()
```

Useful for:

- existing agent runtimes
- workflow engines
- delayed outcome reporting
- reconciliation after execution

---

### Simulations

Inspect prediction vs reality for a specific decision or domain.

```python
comparison = client.simulations.compare(request_id="req_abc123")
print(comparison["predicted_risk"])
print(comparison["actual_outcome"])
print(comparison["calibration_error"])

accuracy = client.simulations.accuracy(domain="customer_transactions")
```

Simulation data becomes more useful when paired with real outcomes.

---

### Learning controls

Trigger recomputation of learning artifacts when needed.

```python
job = client.learning.recompute(domain="customer_transactions", async_mode=True)
print(job["job_id"])

strategy = client.learning.strategy()
print(strategy["strategy_version"])
```

Useful for:

- backfills
- strategy upgrades
- replay experiments
- offline learning refresh

---

### Async client

All major SDK operations are available asynchronously.

```python
from bighub import AsyncBighubClient

async with AsyncBighubClient(api_key="your_api_key") as client:
    result = await client.actions.submit(
        action="refund_full",
        value=450.0,
        domain="customer_transactions",
    )

    if result["recommendation"] in ("proceed", "proceed_with_caution"):
        await execute_refund()
        await client.outcomes.report(
            request_id=result["request_id"],
            status="SUCCESS",
        )
```

---

### Auth

```python
from bighub import BighubClient

# API key, recommended for agents and backend services
client = BighubClient(api_key="bh_live_xxx")

# Bearer token, useful for user sessions
client = BighubClient(bearer_token="eyJhbG...")
```

---

### Error handling

```python
from bighub import BighubAPIError, BighubAuthError

try:
    result = client.actions.submit(action="update_price", value=500)
except BighubAuthError:
    print("Invalid API key")
except BighubAPIError as e:
    print(e.status_code, e.message, e.request_id)
```

All API errors include `request_id` for tracing.

---

### Reliability

Built-in reliability features include:

- automatic retries on 408, 429, and 5xx responses
- configurable timeout, default 15s
- idempotency key support on write operations
- context manager support for clean resource cleanup

---

## Free Beta

Current active plan:

- 3 agents
- 2,500 actions / month
- 30 days history
- 1 environment

The current goal is to make the full decision loop easy to test with real agent actions and real outcomes.

---

## One-Liner

BIGHUB helps agent actions get better recommendations over time by learning from real outcomes.

---

## Links

- [bighub.io](https://bighub.io)
- [GitHub — bighub-io/bighub](https://github.com/bighub-io/bighub)
- [PyPI — bighub-openai](https://pypi.org/project/bighub-openai/)
- [PyPI — bighub (core SDK)](https://pypi.org/project/bighub/)
- [npm — @bighub/bighub-mcp](https://www.npmjs.com/package/@bighub/bighub-mcp)

---

## License

MIT
