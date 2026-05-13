from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..types import JSONDict


def _stable_sha256(payload: JSONDict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


@dataclass
class DecisionPacket:
    """Structured context BIGHUB uses to turn a proposed IT action into a better decision."""

    intent: Optional[str] = None
    action_type: Optional[str] = None
    system: Optional[str] = None
    environment: Optional[str] = None
    context: JSONDict = field(default_factory=dict)
    constraints: List[Any] = field(default_factory=list)
    system_state: JSONDict = field(default_factory=dict)
    candidate_actions: List[Any] = field(default_factory=list)
    rejected_actions: List[Any] = field(default_factory=list)
    risk_factors: List[Any] = field(default_factory=list)
    precedents: List[Any] = field(default_factory=list)
    expected_outcomes: List[Any] = field(default_factory=list)
    verification_plan: List[Any] = field(default_factory=list)
    obligations: List[Any] = field(default_factory=list)
    learning_hooks: List[Any] = field(default_factory=list)
    packet_sha256: Optional[str] = None
    packet_sha256_is_local: bool = False
    raw: JSONDict = field(default_factory=dict)

    @classmethod
    def build(
        cls,
        *,
        action: str,
        context: Optional[JSONDict] = None,
        objective: str = "better_decision",
        system: Optional[str] = None,
        environment: Optional[str] = None,
        constraints: Optional[List[Any]] = None,
        candidate_actions: Optional[List[Any]] = None,
    ) -> "DecisionPacket":
        ctx = dict(context or {})
        packet = cls(
            intent=objective,
            action_type=str(ctx.get("action_type") or ctx.get("type") or "it_action"),
            system=str(system or ctx.get("system") or ctx.get("domain") or "") or None,
            environment=str(environment or ctx.get("environment") or "") or None,
            context=ctx,
            constraints=list(constraints or ctx.get("constraints") or []),
            candidate_actions=list(candidate_actions or [action]),
        )
        packet.packet_sha256 = packet.compute_sha256()
        packet.packet_sha256_is_local = True
        return packet

    @classmethod
    def from_payload(
        cls,
        payload: Optional[JSONDict],
        *,
        proposed_action: str = "",
        context: Optional[JSONDict] = None,
    ) -> "DecisionPacket":
        data = dict(payload or {})
        if not data:
            return cls(context=dict(context or {}))

        ctx = data.get("context")
        if not isinstance(ctx, dict):
            ctx = context or {}

        packet = cls(
            intent=_optional_str(data.get("intent") or data.get("goal") or data.get("objective")),
            action_type=_optional_str(data.get("action_type") or data.get("type")),
            system=_optional_str(data.get("system") or data.get("operational_system") or ctx.get("system")),
            environment=_optional_str(data.get("environment") or ctx.get("environment")),
            context=dict(ctx),
            constraints=_as_list(data.get("constraints")),
            system_state=dict(data.get("system_state") or data.get("world_state") or {}),
            candidate_actions=_as_list(data.get("candidate_actions")),
            rejected_actions=_as_list(data.get("rejected_actions")),
            risk_factors=_as_list(data.get("risk_factors") or data.get("warnings")),
            precedents=_as_list(data.get("precedents")),
            expected_outcomes=_as_list(data.get("expected_outcomes") or data.get("outcomes")),
            verification_plan=_as_list(data.get("verification_plan")),
            obligations=_as_list(data.get("obligations") or data.get("open_obligations")),
            learning_hooks=_as_list(data.get("learning_hooks")),
            packet_sha256=_optional_str(data.get("packet_sha256") or data.get("sha256")),
            raw=data,
        )
        if not packet.packet_sha256:
            packet.packet_sha256 = packet.compute_sha256()
            packet.packet_sha256_is_local = True
        return packet

    def to_dict(self) -> JSONDict:
        payload: JSONDict = {
            "intent": self.intent,
            "action_type": self.action_type,
            "system": self.system,
            "environment": self.environment,
            "context": self.context,
            "constraints": self.constraints,
            "system_state": self.system_state,
            "candidate_actions": self.candidate_actions,
            "rejected_actions": self.rejected_actions,
            "risk_factors": self.risk_factors,
            "precedents": self.precedents,
            "expected_outcomes": self.expected_outcomes,
            "verification_plan": self.verification_plan,
            "obligations": self.obligations,
            "learning_hooks": self.learning_hooks,
            "packet_sha256": self.packet_sha256,
        }
        return payload

    def compute_sha256(self) -> str:
        payload = self.to_dict()
        payload.pop("packet_sha256", None)
        return _stable_sha256(payload)


def _optional_str(value: Any) -> Optional[str]:
    if value in (None, ""):
        return None
    return str(value)
