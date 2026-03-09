from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from .types import JSONDict


@runtime_checkable
class PayloadModel(Protocol):
    def to_payload(self) -> JSONDict:
        ...


def to_payload(value: JSONDict | PayloadModel) -> JSONDict:
    if isinstance(value, dict):
        return value
    return value.to_payload()


def _clean_none(data: JSONDict) -> JSONDict:
    return {k: v for k, v in data.items() if v is not None}


@dataclass
class ActionSubmitV2Model:
    action: str
    actor: str = "AI_AGENT"
    value: Optional[float] = None
    target: Optional[str] = None
    domain: Optional[str] = None
    metadata: Optional[JSONDict] = None

    def to_payload(self) -> JSONDict:
        return _clean_none(asdict(self))


@dataclass
class RuleCreateModel:
    name: str
    domain: str
    max_per_day: int
    max_value: float
    require_approval_above: Optional[float] = None
    min_value: Optional[float] = None
    max_per_hour: Optional[int] = None
    cooldown_seconds: Optional[int] = None
    allowed_hours_start: Optional[int] = None
    allowed_hours_end: Optional[int] = None
    tags: Optional[List[str]] = None
    metadata: Optional[JSONDict] = None

    def to_payload(self) -> JSONDict:
        return _clean_none(asdict(self))


@dataclass
class RuleUpdateModel:
    name: Optional[str] = None
    domain: Optional[str] = None
    max_per_day: Optional[int] = None
    max_value: Optional[float] = None
    require_approval_above: Optional[float] = None
    min_value: Optional[float] = None
    max_per_hour: Optional[int] = None
    cooldown_seconds: Optional[int] = None
    allowed_hours_start: Optional[int] = None
    allowed_hours_end: Optional[int] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[JSONDict] = None

    def to_payload(self) -> JSONDict:
        return _clean_none(asdict(self))


@dataclass
class RuleValidateModel:
    action: str
    actor: str = "AI_AGENT"
    value: Optional[float] = None
    rule_id: Optional[str] = None
    metadata: Optional[JSONDict] = None
    dry_run: Optional[bool] = None

    def to_payload(self) -> JSONDict:
        return _clean_none(asdict(self))


@dataclass
class WebhookCreateModel:
    url: str
    label: str = "default"
    events: Optional[List[str]] = None
    symbols: Optional[List[str]] = None
    intervals: Optional[List[str]] = None
    timeout_seconds: Optional[int] = None
    max_retries: Optional[int] = None
    retry_delay_seconds: Optional[int] = None

    def to_payload(self) -> JSONDict:
        return _clean_none(asdict(self))


@dataclass
class WebhookUpdateModel:
    url: Optional[str] = None
    label: Optional[str] = None
    events: Optional[List[str]] = None
    symbols: Optional[List[str]] = None
    intervals: Optional[List[str]] = None
    is_active: Optional[bool] = None

    def to_payload(self) -> JSONDict:
        return _clean_none(asdict(self))


@dataclass
class APIKeyCreateModel:
    label: str = "default"
    scopes: Optional[List[str]] = None
    rate_limit_per_minute: Optional[int] = None
    ip_whitelist: Optional[List[str]] = None
    expires_in_days: Optional[int] = None

    def to_payload(self) -> JSONDict:
        return _clean_none(asdict(self))


@dataclass
class AuthCredentialsModel:
    email: str
    password: str

    def to_payload(self) -> JSONDict:
        return asdict(self)


@dataclass
class ApprovalResolveModel:
    resolution: str
    comment: Optional[str] = None

    def to_payload(self) -> JSONDict:
        return _clean_none(asdict(self))
