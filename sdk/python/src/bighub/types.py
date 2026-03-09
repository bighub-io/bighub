from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


JSONDict = Dict[str, Any]


class AuthTokens(TypedDict):
    token_type: str
    access_token: str
    refresh_token: str
    user_id: int
    role: str


class RefreshTokenPayload(TypedDict):
    refresh_token: str


class ActionSubmitRequest(TypedDict, total=False):
    action: str
    value: float
    target: str
    actor: str
    domain: str
    metadata: JSONDict


class ActionSubmitV2Request(TypedDict, total=False):
    action: str
    value: float
    target: str
    actor: str
    domain: str
    metadata: JSONDict


class ActionSubmitResponse(TypedDict, total=False):
    allowed: bool
    result: str
    reason: str
    request_id: str
    blocked_by: Optional[str]
    risk_score: float
    validation_hash: str
    requires_approval: bool


class FutureMemoryEvent(TypedDict, total=False):
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


class FutureMemoryIngestRequest(TypedDict, total=False):
    source: str
    source_version: str
    actor: str
    domain: str
    model: str
    trace_id: str
    redact: bool
    redaction_policy: str
    events: List[FutureMemoryEvent]


class FutureMemoryRecommendationsRequest(TypedDict, total=False):
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


class RuleResponse(TypedDict, total=False):
    rule_id: str
    name: str
    domain: str
    status: str
    version: int
    max_per_day: int
    max_value: float
    require_approval_above: Optional[float]


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


class EventItem(TypedDict, total=False):
    event_id: str
    event_type: str
    severity: str
    domain: str
    action: str
    reason: str
    created_at: str


class EventsListResponse(TypedDict, total=False):
    events: List[EventItem]
    total: int
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
