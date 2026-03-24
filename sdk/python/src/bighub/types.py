from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


JSONDict = Dict[str, Any]


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════════


class AuthTokens(TypedDict):
    token_type: str
    access_token: str
    refresh_token: str
    user_id: int
    role: str


class RefreshTokenPayload(TypedDict):
    refresh_token: str


# ═══════════════════════════════════════════════════════════════════════════════
# ACTIONS — REQUEST TYPES
# ═══════════════════════════════════════════════════════════════════════════════


class ActionSubmitRequest(TypedDict, total=False):
    action: str
    value: float
    target: str
    actor: str
    domain: str
    context: JSONDict
    metadata: JSONDict


class ActionSubmitPayloadRequest(TypedDict, total=False):
    action: str
    value: float
    target: str
    actor: str
    domain: str
    context: JSONDict
    metadata: JSONDict


class LiveConnectRequest(TypedDict, total=False):
    actor: str
    context: JSONDict


class LiveHeartbeatRequest(TypedDict, total=False):
    connection_id: str
    context: JSONDict


# ═══════════════════════════════════════════════════════════════════════════════
# ACTIONS — INTELLIGENCE SUB-TYPES
#
# These mirror the backend SubmitActionResponse sub-models.
# Every field the API can return is represented here so developers
# get full autocompletion and type-safety.
# ═══════════════════════════════════════════════════════════════════════════════


class ImpactSummaryDict(TypedDict, total=False):
    blast_radius_p50: int
    blast_radius_p95: int
    blast_radius_max: int
    worst_case_recovery_time_s: float
    irreversibility_risk: float
    cascading_domain_risk: float


class SimulationLiteDict(TypedDict, total=False):
    scenarios_run: int
    fragility_score: float
    confidence: float
    failure_rate: float
    impact_summary: ImpactSummaryDict


class ConfidenceDict(TypedDict, total=False):
    score: float
    level: str
    novel_situation: bool
    reason: str


class CounterfactualDict(TypedDict, total=False):
    available: bool
    easiest_change: Optional[str]
    would_allow: bool


class CreditScoreDict(TypedDict, total=False):
    score: int
    level: str


class SimulationInfoDict(TypedDict, total=False):
    available: bool
    scenarios_run: int
    failure_rate: float
    fragility_score: float
    confidence: float
    tail_risk_level: Optional[str]
    impact_summary: ImpactSummaryDict


class PrecedentDict(TypedDict, total=False):
    total_precedents: int
    with_outcomes: int
    success_rate: float
    negative_rate: float
    risk_level: str
    confidence: float
    warnings: List[str]
    risk_adjustment: float


class IntelligenceDict(TypedDict, total=False):
    confidence: ConfidenceDict
    counterfactual: CounterfactualDict
    credit_score: CreditScoreDict
    simulation: SimulationInfoDict
    precedents: PrecedentDict
    decision_memory: JSONDict


class AlternativeActionDict(TypedDict, total=False):
    action: str
    rationale: str
    estimated_risk: float


class AdvisoryIntelligenceDict(TypedDict, total=False):
    projected_regret: float
    evidence_status: str
    trajectory_health: Optional[str]
    alternatives: List[AlternativeActionDict]
    rationale: str
    rule_basis: Optional[str]
    simulation_summary: JSONDict


# ═══════════════════════════════════════════════════════════════════════════════
# ACTIONS — EVALUATE RESPONSE
#
# The canonical response from POST /actions/evaluate.
#
# Primary output is the `recommendation` — a structured advisory signal.
# The agent (or orchestrator) decides how to act on it.
#
# Legacy enforcement fields (allowed, result) reflect what WOULD be enforced
# if enforcement_mode were 'enforced'.  In 'advisory' mode the agent has
# the final say.
# ═══════════════════════════════════════════════════════════════════════════════


class ActionEvaluateResponse(TypedDict, total=False):

    # ── Decision Intelligence (primary output) ──────────────────────
    #
    # recommendation values:
    #   proceed | proceed_with_caution | review_recommended | do_not_proceed
    recommendation: str
    recommendation_confidence: str
    risk_score: float
    enforcement_mode: str
    enforced_verdict: Optional[str]
    decision_intelligence: AdvisoryIntelligenceDict

    # ── Enforcement layer (legacy / enforced-mode fields) ───────────
    allowed: bool
    result: str
    reason: str
    blocked_by: Optional[str]
    requires_approval: bool

    # ── Metadata ────────────────────────────────────────────────────
    request_id: str
    usage: JSONDict
    warnings: List[str]
    dry_run: bool

    # ── Action Gate additions ───────────────────────────────────────
    mode: str
    intelligence: IntelligenceDict
    max_percentage: Optional[float]
    duration: Optional[str]
    human_review: bool
    gate_version: str

    # ── Learning-influenced verdict ─────────────────────────────────
    verdict_changed: bool
    learning_influenced: bool
    verdict_override: JSONDict


ActionSubmitResponse = ActionEvaluateResponse


# ═══════════════════════════════════════════════════════════════════════════════
# DECISION MEMORY (formerly "Future Memory")
# ═══════════════════════════════════════════════════════════════════════════════


class DecisionMemoryEvent(TypedDict, total=False):
    event_id: str
    seq: int
    schema_version: int
    source_version: str
    tool: str
    status: str
    decision: JSONDict
    arguments: JSONDict
    call_id: str
    output: Any
    error: str
    timestamp: str


FutureMemoryEvent = DecisionMemoryEvent


class DecisionMemoryIngestRequest(TypedDict, total=False):
    source: str
    source_version: str
    actor: str
    domain: str
    model: str
    trace_id: str
    redact: bool
    redaction_policy: str
    events: List[DecisionMemoryEvent]


FutureMemoryIngestRequest = DecisionMemoryIngestRequest


class DecisionMemoryRecommendationsRequest(TypedDict, total=False):
    window_hours: int
    scope: JSONDict
    tool: str
    domain: str
    actor: str
    source: str
    min_events: int
    min_blocked_rate: float
    min_approval_rate: float
    min_tool_error_rate: float
    limit_recommendations: int
    include_examples: bool
    auto_apply: bool


FutureMemoryRecommendationsRequest = DecisionMemoryRecommendationsRequest


# ═══════════════════════════════════════════════════════════════════════════════
# OUTCOMES
# ═══════════════════════════════════════════════════════════════════════════════


class OutcomeReportRequest(TypedDict, total=False):
    status: str
    request_id: str
    case_id: str
    validation_id: str
    description: str
    details: JSONDict
    actual_impact: JSONDict
    correction_needed: bool
    correction_description: str
    correction_cost: Optional[float]
    time_to_detect_s: Optional[float]
    time_to_resolve_s: Optional[float]
    rollback_performed: bool
    revenue_impact: Optional[float]
    customer_impact_count: int
    support_tickets_created: int
    observed_at: Optional[str]
    reported_by: str
    tags: List[str]


class OutcomeDecisionContext(TypedDict, total=False):
    domain: str
    tool: str
    action: str
    actor_type: str
    verdict_was: str
    risk_score_was: float


class OutcomeCorrectionInfo(TypedDict, total=False):
    needed: bool
    description: str
    cost: Optional[float]
    time_to_detect_s: Optional[float]
    time_to_resolve_s: Optional[float]


class OutcomeBusinessImpact(TypedDict, total=False):
    revenue_impact: Optional[float]
    customer_impact_count: int
    support_tickets_created: int


class OutcomeCalibrationInfo(TypedDict, total=False):
    error: Optional[float]
    prediction_correct: Optional[bool]


class OutcomeReportResponse(TypedDict, total=False):
    outcome_id: str
    org_id: str
    request_id: str
    case_id: str
    status: str
    category: str
    severity: float
    reported_at: str
    reported_by: str
    report_source: str
    description: str
    decision_context: OutcomeDecisionContext
    decision_at: Optional[str]
    observed_at: Optional[str]
    time_to_outcome_s: Optional[float]
    details: JSONDict
    actual_impact: JSONDict
    correction: OutcomeCorrectionInfo
    rollback: JSONDict
    business_impact: OutcomeBusinessImpact
    calibration: OutcomeCalibrationInfo
    tags: List[str]


# ═══════════════════════════════════════════════════════════════════════════════
# RULES
# ═══════════════════════════════════════════════════════════════════════════════


class RuleResponse(TypedDict, total=False):
    rule_id: str
    name: str
    description: Optional[str]
    domain: str
    max_per_day: int
    max_value: float
    require_approval_above: Optional[float]
    min_value: Optional[float]
    max_per_hour: Optional[int]
    cooldown_seconds: Optional[int]
    allowed_hours_start: Optional[int]
    allowed_hours_end: Optional[int]
    status: str
    usage_today: int
    usage_total: int
    blocked_today: int
    blocked_total: int
    remaining_today: int
    domain_label: str
    max_value_label: str
    unit: str
    last_used_at: Optional[str]
    created_at: str
    updated_at: str
    tags: List[str]
    version: Optional[int]


class RuleCreateRequest(TypedDict, total=False):
    name: str
    domain: str
    max_per_day: int
    max_value: float
    require_approval_above: float
    min_value: float
    max_per_hour: int
    cooldown_seconds: int
    allowed_hours_start: int
    allowed_hours_end: int
    tags: List[str]
    metadata: JSONDict


class RuleUpdateRequest(TypedDict, total=False):
    name: str
    domain: str
    max_per_day: int
    max_value: float
    require_approval_above: float
    min_value: float
    max_per_hour: int
    cooldown_seconds: int
    allowed_hours_start: int
    allowed_hours_end: int
    status: str
    tags: List[str]
    metadata: JSONDict


class RuleValidateRequest(TypedDict, total=False):
    action: str
    value: float
    actor: str
    rule_id: str
    metadata: JSONDict
    dry_run: bool


class DomainInfo(TypedDict, total=False):
    id: str
    name: str
    max_per_day_default: int
    max_value_default: float
    max_value_label: str
    unit: str


# Public surface rename: constraints (backward-compatible aliases to rule shapes).
ConstraintResponse = RuleResponse
ConstraintCreateRequest = RuleCreateRequest
ConstraintUpdateRequest = RuleUpdateRequest
ConstraintValidateRequest = RuleValidateRequest


# ═══════════════════════════════════════════════════════════════════════════════
# WEBHOOKS
# ═══════════════════════════════════════════════════════════════════════════════


class WebhookCreateRequest(TypedDict, total=False):
    url: str
    label: str
    events: List[str]
    symbols: List[str]
    intervals: List[str]
    timeout_seconds: int
    max_retries: int
    retry_delay_seconds: int


class WebhookUpdateRequest(TypedDict, total=False):
    url: str
    label: str
    events: List[str]
    symbols: List[str]
    intervals: List[str]
    is_active: bool


class WebhookInfo(TypedDict, total=False):
    webhook_id: str
    url: str
    label: str
    events: List[str]
    is_active: bool
    created_at: str


# ═══════════════════════════════════════════════════════════════════════════════
# API KEYS
# ═══════════════════════════════════════════════════════════════════════════════


class APIKeyCreateRequest(TypedDict, total=False):
    label: str
    scopes: List[str]
    rate_limit_per_minute: int
    ip_whitelist: List[str]
    expires_in_days: int


class APIKeyCreateResponse(TypedDict, total=False):
    key: str
    key_id: str
    key_prefix: str
    label: str
    scopes: List[str]
    created_at: str
    expires_at: Optional[str]


# ═══════════════════════════════════════════════════════════════════════════════
# EVENTS & APPROVALS
# ═══════════════════════════════════════════════════════════════════════════════


class EventItem(TypedDict, total=False):
    event_id: str
    event_type: str
    severity: str
    rule_id: Optional[str]
    rule_name: Optional[str]
    domain: Optional[str]
    validation_id: Optional[str]
    action: Optional[str]
    actor: Optional[str]
    value: Optional[float]
    allowed: Optional[bool]
    reason: str
    blocked_by: Optional[str]
    usage: JSONDict
    risk_score: Optional[float]
    validation_hash: Optional[str]
    warnings: Optional[List[str]]
    mode: Optional[str]
    intelligence: JSONDict
    max_percentage: Optional[float]
    duration: Optional[str]
    human_review: Optional[bool]
    gate_version: Optional[str]
    recommendation: Optional[str]
    recommendation_confidence: Optional[str]
    enforcement_mode: Optional[str]
    enforced_verdict: Optional[str]
    decision_intelligence: JSONDict
    recommendation_followed: Optional[bool]
    outcome_status: Optional[str]
    outcome_reported_at: Optional[str]
    created_at: str


class EventsListResponse(TypedDict, total=False):
    events: List[EventItem]
    total: Optional[int]
    limit: int
    offset: int


class ApprovalItem(TypedDict, total=False):
    request_id: str
    rule_id: str
    validation_id: str
    action: str
    actor: str
    value: Optional[float]
    status: str
    created_at: str


# ═══════════════════════════════════════════════════════════════════════════════
# ACTIONS — RESPONSE SUB-TYPES
# ═══════════════════════════════════════════════════════════════════════════════


class ValidationVerifyResponse(TypedDict, total=False):
    valid: bool
    validation_id: str
    validation_hash: Optional[str]
    computed_hash: Optional[str]
    validated_at: Optional[str]
    allowed: Optional[bool]
    result: Optional[str]
    message: str


class ObserverStatsResponse(TypedDict, total=False):
    insight: str
    today: JSONDict
    week: JSONDict
    month: JSONDict
    all_time: JSONDict
    top_blocked_by: List[JSONDict]
    automation_health_score: int


class DashboardSummaryResponse(TypedDict, total=False):
    blocked_this_month: int
    value_protected: float
    approvals_resolved: int
    automation_health_score: int
    total_validations_this_month: int
    allowed_this_month: int
    pending_approvals: int
    today: JSONDict
    week: JSONDict
    insight: str


class ValueProtectedHistoryPoint(TypedDict, total=False):
    date: str
    value_protected: float
    blocked_count: int


class ValueProtectedHistoryResponse(TypedDict, total=False):
    data: List[ValueProtectedHistoryPoint]
    total_value_protected: float
    total_blocked: int
    period_days: int


# ═══════════════════════════════════════════════════════════════════════════════
# DECISION MEMORY — RESPONSE TYPES
# ═══════════════════════════════════════════════════════════════════════════════


class MemoryIngestResponse(TypedDict, total=False):
    accepted: int
    total_stored: int
    source: str


class MemoryContextResponse(TypedDict, total=False):
    org_id: int
    window_hours: int
    filters: JSONDict
    total_events: int
    blocked_rate: float
    approval_rate: float
    tool_error_rate: float
    avg_risk_score: float
    top_tools: List[JSONDict]
    top_block_reasons: List[JSONDict]
    recent_events: List[JSONDict]


class MemoryRefreshResponse(TypedDict, total=False):
    refreshed: bool
    mode: str


class MemoryRecommendationsResponse(TypedDict, total=False):
    org_id: int
    plan: str
    window_hours: int
    generated_at: str
    filters: JSONDict
    summary: JSONDict
    recommendations: List[JSONDict]


# ═══════════════════════════════════════════════════════════════════════════════
# LIVE CONNECTIONS
# ═══════════════════════════════════════════════════════════════════════════════


class LiveConnectionResponse(TypedDict, total=False):
    connection_id: str
    agent_id: str
    current_connections: int
    max_connections: int
    ttl_seconds: int
    heartbeat_interval_seconds: int
    status: str


# ═══════════════════════════════════════════════════════════════════════════════
# TRAJECTORY
#
# These mirror the backend trajectory engine models.
# Trajectory tracks the full multi-step decision journey of an agent session.
# ═══════════════════════════════════════════════════════════════════════════════


class ForecastResultDict(TypedDict, total=False):
    action: str
    immediate_outcome_score: float
    projected_risk_1: float
    projected_risk_3: float
    projected_cost_1: float
    projected_cost_3: float
    projected_recovery_difficulty: float
    projected_incident_probability: float
    projected_escalation_probability: float
    projected_regret: float
    confidence: float
    explanation: List[str]


class DecisionBranchScoreDict(TypedDict, total=False):
    branch: str
    action: str
    projected_value: float
    projected_risk: float
    projected_cost: float
    projected_regret: float
    confidence: float
    rationale: List[str]


class RoutingVerdictDict(TypedDict, total=False):
    verdict: str
    confidence: float
    uncertainty_level: float
    primary_reason: str
    contributing_factors: List[str]
    forecast: ForecastResultDict
    best_branch: DecisionBranchScoreDict
    constraints: List[str]
    trajectory_context: JSONDict
    trajectory_id: Optional[str]
    shadow: bool


class TrajectoryStateDict(TypedDict, total=False):
    trajectory_id: str
    agent_id: str
    org_id: str
    step_index: int
    cumulative_cost: float
    cumulative_risk: float
    cumulative_score: float
    verification_debt: float
    sensitivity_exposure: float
    permission_exposure: float
    reversal_difficulty: float
    irreversible_actions_count: int
    recent_failures_count: int
    recent_escalations_count: int
    consecutive_risky_actions: int
    uncertainty_score: float
    mean_confidence: float
    current_goal_progress: float
    evidence_level: int
    evidence_actions_taken: int
    sensitive_actions_without_evidence: int
    in_recovery: bool
    recovery_attempts: int
    last_failure_action: str
    recovery_strategy: str
    drift_score: float
    blast_radius: float
    last_n_actions: List[str]
    active_constraints: List[str]
    risk_level: str
    has_debt: bool
    is_drifting: bool


class RecommendationQualityQuadrants(TypedDict, total=False):
    followed_positive: int
    followed_negative: int
    ignored_positive: int
    ignored_negative: int


class RecommendationQualityByDomain(TypedDict, total=False):
    domain: str
    total: int
    followed: int
    ignored: int
    follow_rate: float
    followed_positive: int
    ignored_negative: int


class RecommendationQualityByActor(TypedDict, total=False):
    actor_type: str
    total: int
    followed: int
    ignored: int
    follow_rate: float
    followed_positive: int
    ignored_negative: int


class RecommendationQualityExample(TypedDict, total=False):
    outcome_id: str
    request_id: str
    domain: str
    action: str
    tool: str
    status: str
    verdict_was: str
    risk_score_was: Optional[float]
    reported_at: Optional[str]
    description: str
    recommendation_followed: Optional[bool]
    category: str


class RecommendationQualityExamples(TypedDict, total=False):
    helped: List[RecommendationQualityExample]
    missed: List[RecommendationQualityExample]


class RecommendationQualityResponse(TypedDict, total=False):
    total_with_outcome: int
    follow_rate: Optional[float]
    positive_after_following: Optional[float]
    quadrants: RecommendationQualityQuadrants
    by_domain: List[RecommendationQualityByDomain]
    by_actor: List[RecommendationQualityByActor]
    examples: RecommendationQualityExamples
