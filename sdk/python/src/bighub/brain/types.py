from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from ..types import JSONDict


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


@dataclass
class DecisionBrainResult:
    """DecisionBrain output distilled for SDK users."""

    recommendation: Optional[str] = None
    reasoning_summary: Optional[str] = None
    confidence: Optional[float] = None
    expected_regret: Optional[float] = None
    meta_state: JSONDict = field(default_factory=dict)
    selected_policy: Optional[str] = None
    precedent_count: Optional[int] = None
    world_state_used: Optional[bool] = None
    review_reason: Optional[str] = None
    alternatives: List[Any] = field(default_factory=list)
    recommended_execution_mode: Optional[str] = None
    raw: JSONDict = field(default_factory=dict)

    @classmethod
    def from_response(cls, response: JSONDict, *, execution_mode: str = "") -> "DecisionBrainResult":
        brain = response.get("decision_brain")
        if not isinstance(brain, dict):
            brain = {}
        intelligence = response.get("decision_intelligence")
        if not isinstance(intelligence, dict):
            intelligence = {}
        legacy_intelligence = response.get("intelligence")
        if not isinstance(legacy_intelligence, dict):
            legacy_intelligence = {}

        confidence_value = (
            brain.get("confidence")
            or response.get("confidence")
            or _nested(response, "intelligence", "confidence", "score")
            or _nested(response, "decision_packet", "context", "confidence", "score")
        )
        confidence = _to_optional_float(confidence_value)

        precedents = intelligence.get("precedents") or legacy_intelligence.get("precedents") or {}
        if isinstance(precedents, dict):
            precedent_count = _to_optional_int(precedents.get("total_precedents") or precedents.get("with_outcomes") or precedents.get("found"))
        else:
            precedent_count = None
        if brain.get("precedent_count") is not None:
            precedent_count = _to_optional_int(brain.get("precedent_count"))

        world_state = (
            brain.get("world_state_used")
            or response.get("operational_world_snapshot")
            or response.get("world_state")
            or (response.get("decision_runtime_spine") or {}).get("world_state")
            or (response.get("decision_runtime_spine") or {}).get("modules", {}).get("world_state")
        )

        return cls(
            recommendation=_optional_str(brain.get("recommendation") or response.get("recommendation") or response.get("result")),
            reasoning_summary=_optional_str(
                brain.get("reasoning_summary")
                or intelligence.get("rationale")
                or response.get("reasoning_summary")
                or response.get("reason")
            ),
            confidence=confidence,
            expected_regret=_to_optional_float(brain.get("expected_regret") or intelligence.get("projected_regret") or response.get("expected_regret")),
            meta_state=dict(brain.get("meta_state") if isinstance(brain.get("meta_state"), dict) else (response.get("decision_runtime_spine") or {})) if not isinstance(brain.get("meta_state"), list) else {"items": brain.get("meta_state")},
            selected_policy=_optional_str(brain.get("selected_policy") or intelligence.get("rule_basis") or response.get("selected_policy")),
            precedent_count=precedent_count,
            world_state_used=bool(world_state),
            review_reason=_optional_str(brain.get("review_reason") or response.get("review_reason") or response.get("blocked_by")),
            alternatives=_as_list(brain.get("alternatives") or intelligence.get("alternatives") or response.get("alternatives")),
            recommended_execution_mode=_optional_str(brain.get("recommended_execution_mode") or execution_mode or response.get("execution_mode") or response.get("mode")),
            raw=brain or response,
        )

    def to_dict(self) -> JSONDict:
        return {
            "recommendation": self.recommendation,
            "reasoning_summary": self.reasoning_summary,
            "confidence": self.confidence,
            "expected_regret": self.expected_regret,
            "meta_state": self.meta_state,
            "selected_policy": self.selected_policy,
            "precedent_count": self.precedent_count,
            "world_state_used": self.world_state_used,
            "review_reason": self.review_reason,
            "alternatives": self.alternatives,
            "recommended_execution_mode": self.recommended_execution_mode,
        }


def _optional_str(value: Any) -> Optional[str]:
    if value in (None, ""):
        return None
    return str(value)


def _to_optional_float(value: Any) -> Optional[float]:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_optional_int(value: Any) -> Optional[int]:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _nested(data: JSONDict, *path: str) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current
