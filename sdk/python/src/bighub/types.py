from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict


JSONDict = Dict[str, Any]

SystemProvider = Literal[
    "github",
    "sentry",
    "datadog",
    "aws_cloudtrail",
    "terraform",
    "kubernetes",
    "argocd",
    "gitlab",
    "jenkins",
    "azure",
    "prometheus",
    "grafana",
    "openshift",
]


class SystemConnectionResponse(TypedDict, total=False):
    provider: SystemProvider
    configured: bool
    display_name: Optional[str]
    config: JSONDict
    test: JSONDict
    last_error: Optional[str]
    last_checked_at: Optional[str]
    security_requirements: JSONDict
    credential_audit: JSONDict


class SystemPollScheduleResponse(TypedDict, total=False):
    provider: SystemProvider
    schedule: JSONDict


class SystemPollHistoryResponse(TypedDict, total=False):
    provider: SystemProvider
    history: List[JSONDict]
    limit: int


class SystemPollMetricsResponse(TypedDict, total=False):
    metrics: JSONDict


class SystemPollStatusResponse(TypedDict, total=False):
    enabled: bool
    running: bool
    due_count: int
    metrics: JSONDict


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


class ResponsibleActionDict(TypedDict, total=False):
    action: str
    reason: str
    execution_mode: Optional[str]
    evidence: JSONDict


class ResponsibleActionSpaceDict(TypedDict, total=False):
    available: List[ResponsibleActionDict]
    constrained: List[ResponsibleActionDict]
    forbidden: List[ResponsibleActionDict]
    information_gathering: List[ResponsibleActionDict]


class SalientFactorDict(TypedDict, total=False):
    factor: str
    severity: str
    reason: str
    evidence: Any


class OperationalIntentDict(TypedDict, total=False):
    declared: Optional[str]
    inferred: Optional[str]
    confidence: Optional[float]
    mismatch: bool
    mismatch_reasons: List[str]
    action_family: Optional[str]
    evidence: JSONDict


class AgentOperationalBodyDict(TypedDict, total=False):
    can_touch: List[str]
    can_verify: List[str]
    can_rollback: List[str]
    cannot_observe: List[str]
    requires_human: List[str]
    evidence: JSONDict


class ActionInterpretationLayerDict(TypedDict, total=False):
    raw_action: str
    interpreted_action: str
    action_family: str
    operational_meaning: str
    risk_meaning: List[str]
    domain: Optional[str]
    system: Optional[str]
    environment: Optional[str]
    confidence: Optional[float]
    evidence: JSONDict


class PerformativeContractDict(TypedDict, total=False):
    promise_id: str
    org_id: str
    decision_id: Optional[str]
    intervention_id: Optional[str]
    transition_id: Optional[str]
    source_type: str
    source_id: Optional[str]
    promise_type: str
    promiser_agent: str
    promisee: Optional[str]
    content: str
    system: Optional[str]
    domain: Optional[str]
    tool: Optional[str]
    verifier: Optional[str]
    due_at: Optional[str]
    expires_at: Optional[str]
    status: str
    breach_severity: Optional[str]
    breach_reason: Optional[str]
    evidence: JSONDict
    created_at: Optional[str]
    updated_at: Optional[str]


class CatastrophicCeilingDict(TypedDict, total=False):
    active: bool
    policy: str
    non_learnable: bool
    forced_mode: str
    forced_recommendation: str
    reason: str
    triggers: List[JSONDict]
    evidence: JSONDict


class RegretVectorDict(TypedDict, total=False):
    schema_version: str
    source: str
    scalar_regret: float
    dimensions: JSONDict
    moral_weighted_dimensions: JSONDict
    moral_score: float
    dominant_dimensions: List[str]
    damage_bearers: List[str]
    reversibility: str


class SignalEpistemologyDict(TypedDict, total=False):
    schema_version: str
    summary: JSONDict
    signals: List[JSONDict]
    conflicts: List[JSONDict]
    warnings: List[str]


class SignalManipulationAuditDict(TypedDict, total=False):
    schema_version: str
    active: bool
    manipulation_risk: str
    requires_review: bool
    should_suspend_autonomous_execution: bool
    separation_policy: str
    summary: JSONDict
    roles: JSONDict
    findings: List[JSONDict]
    required_controls: List[str]
    decision_effect: JSONDict
    note: str


class SafeNoveltyLaneDict(TypedDict, total=False):
    schema_version: str
    active: bool
    eligible: bool
    status: str
    reason: str
    novelty_detected: bool
    irreversible_but_high_value_hypothesis: bool
    high_value_hypothesis: Optional[str]
    exploration_budget: JSONDict
    recommended_intervention_mode: str
    conditions: JSONDict
    forbidden_escalations: List[str]
    evidence: JSONDict


# ═══════════════════════════════════════════════════════════════════════════════
# FEDERATED NOOSPHERE
#
# Cross-organization civilizational learning. Patterns published here carry
# no org_id, no transition_id, and no payload — only structurally abstract
# fields and coarse aggregates after k-anonymity filtering.
# ═══════════════════════════════════════════════════════════════════════════════


class FederatedInvariantPatternDict(TypedDict, total=False):
    schema_version: str
    pattern_id: str
    invariant_type: str
    generalized_scope: str
    domains: List[str]
    decision_shapes: List[str]
    prescribed_policy_mode: Optional[str]
    prescribed_policy_controls: List[str]
    contributing_org_count: int
    total_support_count: int
    avg_confidence: Optional[float]
    avg_realized_regret: Optional[float]
    avg_violation_count: Optional[float]
    consensus_score: float
    k_anonymity_status: str
    first_seen_at: Optional[str]
    last_seen_at: Optional[str]
    note: str


class FederatedDisagreementPatternDict(TypedDict, total=False):
    schema_version: str
    pattern_id: str
    disagreement_type: str
    decision_shapes: List[str]
    domains: List[str]
    systems: List[str]
    contributing_org_count: int
    total_records: int
    winners: JSONDict
    civilizational_winner: Optional[str]
    consensus_strength: float
    avg_realized_regret: Optional[float]
    avg_regret_reduction: Optional[float]
    k_anonymity_status: str
    first_seen_at: Optional[str]
    last_seen_at: Optional[str]
    note: str


class FederatedBreachPatternDict(TypedDict, total=False):
    schema_version: str
    pattern_id: str
    promise_type: str
    contributing_org_count: int
    total_promises: int
    total_breaches: int
    breach_rate: float
    severity_distribution: JSONDict
    domains: List[str]
    k_anonymity_status: str
    first_seen_at: Optional[str]
    last_seen_at: Optional[str]
    note: str


class FederatedNoosphereSummaryDict(TypedDict, total=False):
    schema_version: str
    contributing_org_count: int
    invariant_pattern_count: int
    disagreement_pattern_count: int
    breach_pattern_count: int
    suppressed_invariant_patterns: int
    suppressed_disagreement_patterns: int
    suppressed_breach_patterns: int
    k_anonymity_threshold: int
    min_total_support: int
    privacy_policy: str
    note: str


class FederatedNoosphereSnapshotResponse(TypedDict, total=False):
    schema_version: str
    summary: FederatedNoosphereSummaryDict
    invariant_patterns: List[FederatedInvariantPatternDict]
    disagreement_patterns: List[FederatedDisagreementPatternDict]
    breach_patterns: List[FederatedBreachPatternDict]


class FederatedContributionResponse(TypedDict, total=False):
    schema_version: str
    org_id: str
    invariant_count: int
    disagreement_count: int
    promise_count: int
    contributed_at: str
    note: str


class FederatedApplicabilityVerdictDict(TypedDict, total=False):
    schema_version: str
    pattern_id: str
    pattern_kind: str
    org_id: str
    status: str
    profile_match_score: float
    domain_match: bool
    shape_match: bool
    local_support_count: int
    local_invariants_supporting: int
    local_disagreements_supporting: int
    contributing_org_count: int
    civilizational_consensus: float
    reasons: List[str]
    recommended_local_test: Optional[JSONDict]
    note: str
    evaluated_at: str


class FederatedApplicabilityReportDict(TypedDict, total=False):
    schema_version: str
    org_id: str
    invariant_pattern_count: int
    disagreement_pattern_count: int
    applicable_count: int
    applicable_with_review_count: int
    not_applicable_count: int
    insufficient_local_data_count: int
    verdicts: List[FederatedApplicabilityVerdictDict]


class FederatedApplicabilityVerdictResponse(TypedDict, total=False):
    schema_version: str
    org_id: str
    verdict: FederatedApplicabilityVerdictDict


class FederatedApplicabilityReportResponse(TypedDict, total=False):
    schema_version: str
    org_id: str
    report: FederatedApplicabilityReportDict


class DisagreementMetricsResponse(TypedDict, total=False):
    org_id: str
    total_records: int
    observed_records: int
    unknown_winner: int
    by_winner: JSONDict
    by_disagreement_type: JSONDict
    llm_over_approval_count: int
    llm_over_approval_rate: float
    bighub_regret_reduction_count: int
    bighub_regret_reduction_rate: float
    human_override_success_count: int
    human_override_success_rate: float
    human_overblock_count: int
    human_overblock_rate: float
    bighub_false_positive_count: int
    bighub_false_positive_rate: float
    bighub_false_negative_count: int
    bighub_false_negative_rate: float
    avg_regret_when_bighub_changed_decision: Optional[float]
    avg_regret_when_baseline_path_followed: Optional[float]
    avg_regret_reduction: Optional[float]
    top_llm_over_approval_shapes: List[JSONDict]
    top_bighub_regret_reduction_shapes: List[JSONDict]


class LearningImpactReportResponse(TypedDict, total=False):
    org_id: str
    observed_ctg_edges: int
    transitions_with_learning_tasks: int
    transitions_with_candidates: int
    transitions_with_breakdown_findings: int
    transitions_with_falsification_experiments: int
    transitions_with_promotions: int
    transitions_with_active_learning_recommendations: int
    future_decisions_created_after_observed_edges: int
    future_decisions_learning_influenced: int
    future_decisions_verdict_changed: int
    disagreements_observed: int
    disagreements_by_winner: JSONDict
    disagreements_by_type: JSONDict
    bighub_won_disagreements: int
    human_won_disagreements: int
    llm_won_disagreements: int
    unknown_disagreement_winner: int
    avg_regret_when_bighub_changed_decision: Optional[float]
    avg_regret_when_baseline_path_followed: Optional[float]
    avg_regret_reduction: Optional[float]
    promises_total: int
    promises_kept: int
    promises_breached: int
    promise_keep_rate: Optional[float]
    breaches_by_promise_type: JSONDict
    deontic_registry_summary: JSONDict
    open_deontic_claims: List[JSONDict]
    open_deontic_remedies: List[JSONDict]
    deontic_precedents: List[JSONDict]
    decision_freedom_metrics: JSONDict
    stagnation_risk: Optional[str]
    conservative_pressure_score: Optional[float]
    innovation_saved_count: int
    potential_overconservative_blocks: int
    regret_vector_summary: JSONDict
    top_regret_dimensions: List[JSONDict]
    regret_damage_bearers: JSONDict
    multi_domain_cascade_summary: JSONDict
    top_multi_domain_cascades: List[JSONDict]
    cascade_domain_paths: List[JSONDict]
    examples: List[JSONDict]


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

    # ── Decision Packet v1 ───────────────────────────────────────────
    decision_packet: JSONDict

    # ── Responsible decision surface ─────────────────────────────────
    responsible_action_space: ResponsibleActionSpaceDict
    salient_factors: List[SalientFactorDict]
    signal_epistemology: SignalEpistemologyDict
    signal_manipulation_audit: SignalManipulationAuditDict
    operational_intent: OperationalIntentDict
    agent_operational_body: AgentOperationalBodyDict
    action_interpretation_layer: ActionInterpretationLayerDict
    safe_novelty_lane: SafeNoveltyLaneDict
    performative_contracts: List[PerformativeContractDict]
    catastrophic_ceiling: CatastrophicCeilingDict
    expected_regret_vector: RegretVectorDict


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


class RecommendationQualityTrendPoint(TypedDict, total=False):
    week: Optional[str]
    total: int
    followed: int
    ignored: int
    follow_rate: float
    positive_after_following: Optional[float]
    quadrants: RecommendationQualityQuadrants


class RecommendationQualityResponse(TypedDict, total=False):
    total_with_outcome: int
    follow_rate: Optional[float]
    positive_after_following: Optional[float]
    quadrants: RecommendationQualityQuadrants
    by_domain: List[RecommendationQualityByDomain]
    by_actor: List[RecommendationQualityByActor]
    trend: List[RecommendationQualityTrendPoint]
    examples: RecommendationQualityExamples
