# BIGHUB SDK

Add better decisions to IT agent workflows.

**BIGHUB turns proposed IT agent actions into better decisions before they run.**

BIGHUB takes a proposed IT action, builds a Decision Packet, runs DecisionBrain, selects the right decision path, and returns the better action before execution.

```bash
pip install bighub
```

Python 3.9+. Single dependency: `httpx`.

---

## Table of contents

**Start here**

- [Quick Start](#quick-start)
- [When to use BIGHUB](#when-to-use-bighub)
- [Decision object](#decision-object)
- [Trajectory-aware evaluation](#trajectory-aware-evaluation)
- [Core Loop (detailed)](#core-loop-detailed)

**Why it's different**

- [Outcomes](#outcomes)
- [Recommendation quality](#recommendation-quality)
- [Decision Cases](#decision-cases)
- [Precedents](#precedents)
- [Calibration](#calibration)

**Platform resources**

- [Batch evaluation](#batch-evaluation) · [Dry run](#dry-run) · [Live sessions](#live-sessions) · [Decision memory](#decision-memory) · [Multi-signal retrieval](#multi-signal-retrieval) · [Insights](#insights) · [Simulations](#simulations) · [Runtime ingestion](#runtime-ingestion) · [System integrations](#system-integrations) · [Learning controls](#learning-controls) · [Operating constraints](#operating-constraints) · [Events](#events) · [Approvals](#approvals) · [Webhooks](#webhooks)

**Reference**

- [Async client](#async-client) · [Auth](#auth) · [Error handling](#error-handling) · [Reliability](#reliability) · [API Reference](#api-reference) · [Free Beta](#free-beta) · [Links](#links)

---

## Quick Start

```python
from bighub import Bighub

bighub = Bighub(api_key="your_api_key")

decision = bighub.decide(
    action="Rotate database credentials across production services",
    context={
        "system": "database",
        "environment": "production",
        "services": ["billing", "payments", "auth"],
    },
)

print(decision.better_action)
print(decision.selected_model)
print(decision.mode)
print(decision.risk)

if decision.needs_review:
    decision.request_review()
elif decision.needs_more_context:
    print("More context required:", decision.reason)
elif decision.should_not_run:
    print("Do not run:", decision.reason)
elif decision.can_run:
    action_to_run = decision.better_action or decision.proposed_action
    run(action_to_run)
else:
    print(decision.brain.reasoning_summary)

bighub.close()
```

The core public flow:

**proposed IT action -> selected model -> Decision Packet -> DecisionBrain -> better action -> execution mode -> review if needed**

---

## When to use BIGHUB

Use BIGHUB before IT agent actions such as:

- granting Okta access
- rotating credentials
- deploying or rolling back services
- changing CI/CD or cloud/IAM settings
- exporting sensitive data
- posting incident or support updates
- acting on workflows that need human review

If your agent only reads data or performs idempotent lookups, you probably do not need BIGHUB. It is designed for actions where the right scope, timing, model, and review path matter.

---

## Decision object

`bighub.decide(...)` returns a rich `Decision` object:

| Field | Description |
|---|---|
| `better_action` | A real backend-produced better action when available; otherwise `None` |
| `selected_model` | Model or path BIGHUB selected for the decision |
| `decision_path` | Native BIGHUB, packet + frontier model, review-first, or needs-more-context |
| `packet` | `DecisionPacket`: intent, system context, constraints, candidates, risks, precedents, verification |
| `brain` | `DecisionBrainResult`: reasoning summary, confidence, regret, policy, alternatives |
| `mode` | `autonomous`, `constrained`, `review`, `blocked`, `needs_context`, `shadow`, or `dry_run` |
| `can_run` | Whether your workflow can execute `better_action` now |
| `needs_review` | Whether a human should approve, deny, or modify the action |
| `needs_more_context` | Whether the workflow should collect more context first |
| `should_not_run` | Whether BIGHUB recommends not executing this action |
| `reason` | Convenience read: top-level evaluate **`reason`** when present, otherwise brain **`review_reason`** / **`reasoning_summary`**, otherwise **`model_selection_reason`** |

Legacy `BighubClient` and `client.actions.evaluate(...)` remain available for existing integrations.

For agents and product code that want one polished object instead of the full
normalization layer, use `decision.brief()`:

```python
brief = decision.brief()

if brief.can_run:
    run(brief.recommended_action)
elif brief.needs_review:
    open_review(brief.to_dict())
```

`DecisionBrief` keeps the stable fields most workflows need: recommended action,
mode, review/context/blocking flags, risk, confidence, regret, reason, system,
model/path, world-state usage, verification step count, obligation count, and warnings.

The SDK normalizes real `/actions/evaluate` responses. It does not invent model selection fields: if the backend does not return `selected_model`, `selected_decision_path`, or `model_selection.reason`, the corresponding SDK attributes are `None`. If a backend `decision_packet` has no `packet_sha256`, the SDK computes a stable local hash and marks it with `packet.packet_sha256_is_local=True`.

The SDK also does not invent `better_action`. Use `decision.better_action or decision.proposed_action` only after checking `decision.needs_review`, `decision.needs_more_context`, `decision.should_not_run`, and confirming `decision.can_run`.

Backend field mapping:

| Backend field | SDK field | Fallback |
|---|---|---|
| `request_id`, `validation_id`, `id` | `decision.request_id` | `None` |
| request `action`, raw `action`, runtime spine action | `decision.proposed_action` | `None` |
| `better_action`, `recommended_action`, first alternative action | `decision.better_action` | `None` |
| `selected_model`, `model_selection.selected_model` | `decision.selected_model` | `None` |
| `model_selection.reason`, `model_selection_reason` | `decision.model_selection_reason` | `None` |
| `selected_decision_path`, `decision_path` | `decision.decision_path` | `None` |
| `decision_packet` | `decision.packet` | empty `DecisionPacket` |
| `decision_intelligence`, `intelligence`, runtime spine | `decision.brain` | empty `DecisionBrainResult` |
| `mode`, `execution_mode`, `result`, `recommendation`, `human_review` | `decision.mode` | `None` |
| `risk_score`, `risk` | `decision.risk` | `None` |
| numeric `confidence`, `intelligence.confidence.score` | `decision.confidence` | `None` |
| `decision_intelligence.projected_regret`, runtime spine regret | `decision.expected_regret` | `None` |

---

## Trajectory-aware evaluation

BIGHUB evaluates actions not only in isolation, but also in the context of what happened before. As outcomes accumulate, similar sequences and prior decisions improve future recommendations.

For costly and multi-step workflows, trajectory-aware signals mean the same action may be judged differently depending on what happened earlier in the sequence.

---

## Core Loop (detailed)

### 1) Build a Decision Packet

```python
packet = bighub.build_packet(
    action="Grant temporary Okta admin access to user alice@example.com",
    context={"system": "okta", "environment": "production", "ticket": "INC-8821"},
)

print(packet.packet_sha256)
```

### 2) Run DecisionBrain

```python
brain = bighub.run_brain(packet=packet)

print(brain.recommendation)
print(brain.reasoning_summary)
```

### 3) Use the high-level decision API

```python
decision = bighub.decide(
    action="Grant temporary Okta admin access to user alice@example.com",
    context={"system": "okta", "environment": "production", "ticket": "INC-8821"},
)

if decision.needs_review:
    bighub.reviews.resolve(
        decision.request_id,
        decision="modified",
        better_action="Grant scoped Okta admin access for 2h",
        reason="Reduce duration and scope",
    )
```

### Optional: report outcomes

When outcomes are reported later, BIGHUB can use them to improve future decisions.

```python
decision.report_outcome(
    status="completed",
    evidence={"deployment_id": "dep_123"},
)
```

### 4) Reuse what was learned on future decisions

```python
precedents = bighub.precedents.query(
    domain="it_actions",
    action=decision.proposed_action,
    risk_score=decision.risk,
)

print(precedents["total_precedents"])
print(precedents["outcomes"])
```

---

# Why it's different

The sections below show how BIGHUB closes the learning loop: real outcomes, recommendation quality tracking, decision cases, precedent intelligence, and calibration.

---

## Outcomes

### Report an outcome

```python
client.outcomes.report(
    request_id=result["request_id"],
    status="FAILURE",
    description="Payment processor rejected the refund",
    revenue_impact=-450.0,
    correction_needed=True,
    correction_description="Manual refund required",
    correction_cost=25.0,
    time_to_detect_s=3600,
    time_to_resolve_s=7200,
    rollback_performed=True,
    tags=["payment", "refund"],
)
```

### Report outcomes in batch

```python
client.outcomes.report_batch([
    {"request_id": "act_001", "status": "SUCCESS", "description": "OK"},
    {"request_id": "act_002", "status": "FAILURE", "description": "Timeout"},
])
```

### Retrieve outcomes

```python
outcome = client.outcomes.get("act_abc123")

outcome_v = client.outcomes.get_by_validation("val_xyz789")

outcome_c = client.outcomes.get_by_case("case_456")
```

### Outcome timeline

```python
timeline = client.outcomes.timeline("act_abc123")
```

### Pending outcomes

```python
pending = client.outcomes.pending(min_age_hours=24, limit=100)
```

### Outcome analytics

```python
analytics = client.outcomes.analytics(domain="customer_transactions")

taxonomy = client.outcomes.taxonomy()
```

---

## Recommendation quality

Track whether BIGHUB's recommendations lead to better outcomes:

```python
quality = client.outcomes.recommendation_quality(domain="customer_transactions")

print(quality["follow_rate"])
print(quality["positive_after_following"])
print(quality["quadrants"])   # followed_positive, followed_negative, ignored_positive, ignored_negative
print(quality["trend"])       # weekly time series
```

### Partner view

Self-contained domain view with KPIs, trend, evidence pockets, and examples:

```python
view = client.outcomes.partner_view("customer_transactions")
# overview, recommendation_quality, trend, by_action, sparse_evidence, examples
```

---

## Decision Cases

A DecisionCase connects the proposed action, context, recommendation, and real outcome:

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

### Query and filter cases

```python
cases = client.cases.list(
    domain="customer_transactions",
    has_outcome=True,
    min_risk_score=0.3,
    limit=20,
)

case = client.cases.get("case_abc123")
```

### Case-level precedents and calibration

```python
precedents = client.cases.precedents(
    action="refund_full",
    domain="customer_transactions",
    axes={"reversibility": 0.9},
    min_similarity=0.5,
)

cal = client.cases.calibration(domain="customer_transactions")
```

---

## Precedents

```python
precedents = client.precedents.query(
    domain="customer_transactions",
    action="refund_full",
    risk_score=0.35,
    require_outcome=True,
)

signals = client.precedents.signals(
    domain="customer_transactions",
    action="refund_full",
)

stats = client.precedents.stats()
```

---

## Calibration

Compare prediction vs reality:

```python
report = client.calibration.report(domain="customer_transactions")
print(report["calibration_quality"])
print(report["bias_direction"])

reliability = client.calibration.reliability(domain="customer_transactions")

drift = client.calibration.drift(window_days=14, domain="customer_transactions")

breakdown = client.calibration.breakdown(by="domain")

feedback = client.calibration.feedback(domain="customer_transactions")

history = client.calibration.quality_history(days=30, domain="customer_transactions")
```

### Observe a calibration data point

```python
client.calibration.observe(
    case_id="case_abc123",
    predicted_risk=0.35,
    outcome_status="FRAUD",
    domain="customer_transactions",
)
```

---

# Platform resources

Advanced features for teams that need batch processing, live sessions, memory, simulations, operating constraints, and more.

---

## Batch evaluation

Evaluate multiple actions in a single request:

```python
results = client.actions.evaluate_batch(
    actions=[
        {"action": "refund_full", "value": 200.0, "target": "order_001"},
        {"action": "refund_partial", "value": 50.0, "target": "order_002"},
    ],
    domain="customer_transactions",
    actor="refund_agent",
)

for r in results:
    print(r["recommendation"], r["risk_score"])
```

---

## Dry run

Evaluate without persisting the decision — useful for testing and previewing:

```python
from bighub.models import ActionSubmitPayloadModel

result = client.actions.dry_run(
    payload=ActionSubmitPayloadModel(
        action="delete_account",
        value=0.0,
        domain="account_management",
        actor="cleanup_agent",
    )
)

print(result["recommendation"], result["risk_score"])
```

---

## Live sessions

For long-running agent sessions that need continuous evaluation:

```python
session = client.actions.begin_live_session(actor="trading_agent")

result = session.evaluate(
    action="buy_stock",
    value=10000.0,
    domain="trading",
)

session.heartbeat()

# ... more evaluations ...

session.disconnect()
```

Live sessions track connection state and propagate context across evaluations.

---

## Decision memory

Ingest structured decision events and retrieve context-aware recommendations:

```python
# Ingest runtime decision events
client.actions.ingest_memory(
    events=[
        {"type": "tool_call", "tool": "refund_payment", "result": "success"},
        {"type": "tool_call", "tool": "send_email", "result": "success"},
    ],
    domain="customer_transactions",
    actor="support_agent",
)

# Retrieve memory context
context = client.actions.memory_context(
    domain="customer_transactions",
    window_hours=24,
)

# Get pattern-based recommendations
recs = client.actions.memory_recommendations(
    domain="customer_transactions",
    window_hours=24,
)
```

---

## Multi-signal retrieval

Aggregate precedent retrieval across multiple strategies:

```python
results = client.retrieval.query(
    domain="customer_transactions",
    action="refund_full",
    strategy="balanced",
)

explained = client.retrieval.query_explained(
    domain="customer_transactions",
    action="refund_full",
    strategy="consequence-focused",
)

comparison = client.retrieval.compare(
    domain="customer_transactions",
    action="refund_full",
    strategy_a="balanced",
    strategy_b="consequence-focused",
)

strategies = client.retrieval.strategies()

stats = client.retrieval.stats()
```

---

## Insights

Retrieve learned advisories and risk patterns:

```python
advice = client.insights.advise(
    tool="increase_price",
    action="increase_price",
    domain="customer_transactions",
)

patterns = client.insights.patterns(domain="customer_transactions", min_severity="high")

learn = client.insights.learn()

profile = client.insights.profile(domain="customer_transactions")
```

---

## Simulations

Inspect simulation snapshots and prediction accuracy:

```python
snapshots = client.simulations.list(domain="customer_transactions", with_outcome=True)

snapshot = client.simulations.get("snap_abc123")

by_req = client.simulations.by_request("act_abc123")

comparison = client.simulations.compare("act_abc123")
print(comparison["predicted_risk"])
print(comparison["actual_outcome"])
print(comparison["calibration_error"])

accuracy = client.simulations.accuracy(domain="customer_transactions")

stats = client.simulations.stats()
```

---

## Runtime ingestion

Route structured runtime data into BIGHUB from existing agent runtimes, workflow engines, or delayed pipelines:

```python
client.ingest.event(
    event_type="ACTION_EXECUTED",
    request_id="req_abc123",
    domain="customer_transactions",
    action={"tool": "refund_full", "arguments": {"amount": 450}},
    execution={"executed": True, "status_code": 200},
)

client.ingest.batch([
    {"event_type": "ACTION_EXECUTED", "request_id": "req_001", ...},
    {"event_type": "OUTCOME_OBSERVED", "request_id": "req_002", ...},
])

client.ingest.reconcile(
    key_name="request_id",
    key_value="req_abc123",
    outcome={
        "event_type": "OUTCOME_OBSERVED",
        "outcome": {"status": "SUCCESS", "description": "Charge completed"},
    },
)

lifecycles = client.ingest.lifecycles(status_filter="active", limit=50)

lifecycle = client.ingest.lifecycle(request_id="req_abc123")

pending = client.ingest.pending(limit=50)

stale = client.ingest.stale(stale_after_days=7, limit=50)

stats = client.ingest.stats()
```

---

## System integrations

Manage the systems BIGHUB can poll for operational evidence before decisions:

```python
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
poll = client.systems.poll("gitlab")
metrics = client.systems.poll_metrics()
world = client.systems.world_state()
```

First-class providers: `github`, `sentry`, `datadog`, `aws_cloudtrail`, `terraform`, `kubernetes`, `argocd`, `gitlab`, `jenkins`, `azure`, `prometheus`, `grafana`, and `openshift`.

Each provider also has a convenience object:

```python
client.systems.prometheus.test({"base_url": "https://prom.example.com", "token": "..."})
history = client.systems.kubernetes.history(limit=25)
run_due = client.systems.run_due_polls()
```

Poll snapshots and histories returned by the backend are redacted before persistence and exposure. Polls feed `VerifierResult` rows that appear in `client.systems.world_state()`, so DecisionBrain can see stale/healthy/degraded infrastructure state without callers manually injecting every signal.

---

## Learning controls

Trigger recomputation of learning artifacts when needed:

```python
job = client.learning.recompute(domain="customer_transactions", async_mode=True)
print(job["job_id"])

backfill = client.learning.backfill(domain="customer_transactions", force=True)

strategy = client.learning.strategy()

runs = client.learning.runs(limit=10)
```

---

## Operating constraints

Optional operating limits that inform BIGHUB's recommendations. Enforced only when your runtime adapter supports it.

```python
constraint = client.constraints.create({
    "name": "max_refund_value",
    "domain": "customer_transactions",
    "conditions": {"value_gt": 1000},
    "action_on_match": "review",
})

constraints = client.constraints.list(domain="customer_transactions")

client.constraints.pause(constraint["rule_id"])
client.constraints.resume(constraint["rule_id"])

client.constraints.validate({"domain": "customer_transactions", "action": "refund_full", "value": 500})

domains = client.constraints.domains()

versions = client.constraints.versions(constraint["rule_id"])
```

`client.rules` is a backward-compatible alias for `client.constraints`.

---

## Events

Query the dashboard event stream:

```python
events = client.events.list(event_type="action_allowed", limit=100)

stats = client.events.stats()
```

---

## Approvals

Manage the human-in-the-loop approval queue:

```python
pending = client.approvals.list(status_filter="pending")

resolved = client.approvals.resolve("req_abc123", resolution="approved", comment="Looks good")
```

---

## Webhooks

Configure real-time notifications:

```python
webhook = client.webhooks.create({
    "url": "https://example.com/hook",
    "events": ["signal.new", "outcome.reported"],
})

webhooks = client.webhooks.list()

client.webhooks.test(webhook["webhook_id"])

deliveries = client.webhooks.deliveries(webhook["webhook_id"])

client.webhooks.replay_failed_delivery(webhook["webhook_id"], delivery_id=42)

valid = client.webhooks.verify_signature(
    payload="...", signature="...", secret="...", timestamp=1234567890
)

event_types = client.webhooks.list_events()
```

---

# Reference

---

## Async client

All resources are available asynchronously:

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

## Auth

```python
from bighub import BighubClient

# API key — recommended for agents and backend services
client = BighubClient(api_key="bh_live_xxx")

# Bearer token — useful for user sessions
client = BighubClient(bearer_token="eyJhbG...")
```

---

## Error handling

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

## Reliability

Built-in reliability features:

- Automatic retries on 408, 429, and 5xx responses
- Configurable timeout (default 15s)
- Idempotency key support on write operations
- Context manager support for clean resource cleanup

---

## API Reference

Every method listed below is available on both `BighubClient` (sync) and `AsyncBighubClient` (async).

### `client.actions`

| Method | Description |
|---|---|
| `evaluate(action, value, target, actor, domain, context, metadata, idempotency_key)` | Evaluate an action — returns structured recommendation |
| `submit(...)` | Alias for `evaluate()` |
| `evaluate_payload(payload, idempotency_key)` | Evaluate with a free-form payload dict or model |
| `submit_payload(...)` | Alias for `evaluate_payload()` |
| `dry_run(payload, idempotency_key)` | Non-persistent evaluation (preview) |
| `evaluate_batch(actions, domain, actor)` | Evaluate multiple actions in one request |
| `connect(actor, context)` | Open a live connection slot |
| `heartbeat(connection_id, context)` | Heartbeat a live connection |
| `disconnect(connection_id, context)` | Close a live connection |
| `begin_live_session(actor, context)` | Create a managed live session |
| `ingest_memory(events, source, actor, domain, ...)` | Ingest structured decision memory events |
| `memory_context(window_hours, tool, domain, actor, source, limit_recent)` | Retrieve memory context |
| `memory_recommendations(window_hours, domain, ...)` | Get pattern-based recommendations from memory |
| `refresh_memory_aggregates(concurrent, window_hours)` | Refresh memory aggregates |
| `verify_validation(validation_id)` | Verify a validation hash |
| `value_protected_history(days)` | Value-protected history over time |
| `dashboard_summary()` | Dashboard summary metrics |
| `observer_stats()` | Observer statistics |
| `status()` | Service status |

### `client.outcomes`

| Method | Description |
|---|---|
| `report(status, request_id, case_id, validation_id, description, ...)` | Report a real-world outcome |
| `report_batch(outcomes)` | Batch report outcomes (max 100) |
| `get(request_id)` | Get outcome by request_id |
| `get_by_validation(validation_id)` | Get outcome by validation_id |
| `get_by_case(case_id)` | Get outcome by case_id |
| `timeline(request_id)` | Full outcome timeline for a request |
| `pending(min_age_hours, limit)` | Decisions awaiting outcome reports |
| `analytics(domain, since, until)` | Outcome analytics summary |
| `taxonomy()` | Supported outcome status taxonomy |
| `recommendation_quality(domain, since, until)` | Follow rate, quadrants, trend, by domain/actor |
| `partner_view(domain)` | Self-contained domain view with KPIs and examples |

### `client.cases`

| Method | Description |
|---|---|
| `create(domain, action, verdict, context, simulation, goal_summary, ...)` | Create a decision case |
| `get(case_id)` | Get a case by ID |
| `list(domain, tool, action, verdict, outcome_status, has_outcome, ...)` | List and filter cases |
| `report_outcome(case_id, status, description, ...)` | Report outcome for a case |
| `precedents(action, domain, tool, axes, min_similarity, limit)` | Precedent intelligence for a proposed action |
| `calibration(domain)` | Calibration metrics for cases |

### `client.precedents`

| Method | Description |
|---|---|
| `query(domain, action, tool, risk_score, intent, min_similarity, ...)` | Query similar past cases |
| `signals(domain, action, tool, risk_score)` | Aggregated precedent signals |
| `stats()` | Precedent index statistics |

### `client.retrieval`

| Method | Description |
|---|---|
| `query(domain, action, tool, strategy, axes, risk_score)` | Multi-signal precedent retrieval |
| `query_explained(domain, action, tool, strategy, ...)` | Retrieval with explanation trace |
| `strategies()` | List available retrieval strategies |
| `strategy(name)` | Get details for one strategy |
| `index_case(case_id, org_id, tool, action, domain, ...)` | Manually index a case |
| `compare(domain, action, strategy_a, strategy_b)` | Compare two strategies |
| `stats()` | Retrieval index statistics |

### `client.calibration`

| Method | Description |
|---|---|
| `report(domain, tool, risk_band)` | Calibration report |
| `reliability(domain, tool)` | Reliability diagram data |
| `drift(window_days, domain)` | Calibration drift over time |
| `breakdown(by)` | Calibration breakdown (by domain/tool) |
| `feedback(domain)` | Calibration feedback signals |
| `observe(case_id, predicted_risk, outcome_status, domain, ...)` | Submit a calibration observation |
| `quality_history(days, domain)` | Daily quality score over time |

### `client.insights`

| Method | Description |
|---|---|
| `advise(tool, action, domain, actor_type, risk_band)` | Learned advisories for an action |
| `patterns(pattern_type, domain, tool, min_severity)` | Discovered risk patterns |
| `learn()` | Learning refresh |
| `profile(tool, action, domain)` | Action/tool profile |

### `client.simulations`

| Method | Description |
|---|---|
| `list(domain, tool, with_outcome, limit)` | List simulation snapshots |
| `get(snapshot_id)` | Get a snapshot |
| `by_request(request_id)` | Get snapshot by request |
| `compare(request_id)` | Compare predicted vs actual |
| `accuracy(domain, tool)` | Domain-level accuracy |
| `stats()` | Simulation statistics |

### `client.learning`

| Method | Description |
|---|---|
| `strategy()` | Current learning strategy |
| `runs(limit)` | Recent learning runs |
| `recompute(domain, action_family, force, limit, async_mode)` | Trigger learning recomputation |
| `backfill(domain, action_family, force, limit, async_mode)` | Backfill learning artifacts |

### `client.ingest`

| Method | Description |
|---|---|
| `event(event_type, request_id, domain, action, execution, outcome, ...)` | Ingest a single event |
| `batch(events)` | Ingest events in batch |
| `reconcile(key_name, key_value, outcome)` | Reconcile outcome with existing event |
| `lifecycles(status_filter, limit)` | List event lifecycles |
| `lifecycle(request_id, case_id, external_ref, ...)` | Get lifecycle for one event |
| `pending(limit)` | Events pending reconciliation |
| `stale(stale_after_days, limit)` | Stale unreconciled events |
| `stats()` | Ingestion statistics |

### `client.constraints`

| Method | Description |
|---|---|
| `create(payload, idempotency_key)` | Create a constraint |
| `list(status, domain, limit, offset)` | List constraints |
| `get(rule_id)` | Get a constraint |
| `update(rule_id, payload, idempotency_key)` | Update a constraint |
| `delete(rule_id, idempotency_key)` | Delete a constraint |
| `pause(rule_id)` | Pause a constraint |
| `resume(rule_id)` | Resume a constraint |
| `dry_run(payload)` | Preview constraint without persisting |
| `validate(payload)` | Validate an action against constraints |
| `validate_dry_run(payload)` | Validate (dry run) |
| `domains()` | List domains with constraints |
| `versions(rule_id, limit)` | Constraint version history |
| `apply_patch(rule_id, patch, preview, reason, ...)` | Apply a JSON Patch |
| `purge_idempotency(only_expired, older_than_hours, limit)` | Admin: purge idempotency keys |

### `client.systems`

| Method | Description |
|---|---|
| `list_connections(org_id)` | List configured system integrations |
| `connection(provider, org_id)` | Get one provider connection summary |
| `test_connection(provider, config, org_id)` | Test unsaved provider config |
| `save_connection(provider, config, display_name, org_id)` | Save provider config |
| `delete_connection(provider, org_id)` | Delete provider connection |
| `poll(provider, org_id)` | Trigger one provider poll now |
| `poll_schedule(provider, org_id)` | Get provider poll schedule |
| `update_poll_schedule(provider, enabled, interval_seconds, max_backoff_seconds, org_id)` | Configure provider polling |
| `poll_history(provider, limit, org_id)` | Read redacted provider poll history |
| `poll_status(org_id)` | Scheduler status and due counts |
| `poll_metrics(org_id)` | Provider success/failure, latency, stale schedule and verifier-result metrics |
| `run_due_polls(org_id)` | Run due polls for the current organization |
| `world_state(limit, freshness_minutes, in_flight_minutes)` | Operational world state consumed by decisions |

### `client.events`

| Method | Description |
|---|---|
| `list(event_type, severity, rule_id, limit, offset)` | Query event stream |
| `stats()` | Event statistics |

### `client.approvals`

| Method | Description |
|---|---|
| `list(status_filter, limit)` | List approval requests |
| `resolve(request_id, resolution, comment)` | Resolve an approval |

### `client.webhooks`

| Method | Description |
|---|---|
| `create(payload)` | Create a webhook |
| `list(include_inactive)` | List webhooks |
| `get(webhook_id)` | Get a webhook |
| `update(webhook_id, payload)` | Update a webhook |
| `delete(webhook_id)` | Delete a webhook |
| `deliveries(webhook_id, limit)` | List deliveries |
| `test(webhook_id, event_type)` | Send a test delivery |
| `list_events()` | List subscribable event types |
| `verify_signature(payload, signature, secret, timestamp)` | Verify webhook signature |
| `replay_failed_delivery(webhook_id, delivery_id)` | Replay a failed delivery |

---

## Free Beta

Current active plan:

- 3 agents
- 2,500 actions / month
- 30 days history
- 1 environment

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
