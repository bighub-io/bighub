from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from ..brain.types import DecisionBrainResult
from ..packets.types import DecisionPacket
from ..types import JSONDict

MODES = {"autonomous", "constrained", "review", "blocked", "needs_context", "shadow", "dry_run"}


@dataclass
class ModelSelection:
    """Model/path selection as returned by the backend.

    If the backend does not return model-selection fields, these attributes stay
    ``None``. The SDK deliberately does not infer a model from the request.
    """

    selected_model: Optional[str] = None
    selected_decision_path: Optional[str] = None
    reason: Optional[str] = None
    frontier_required: Optional[bool] = None
    native_possible: Optional[bool] = None
    packet_required: Optional[bool] = None
    review_required: Optional[bool] = None
    raw: JSONDict = field(default_factory=dict)

    @classmethod
    def from_backend_response(cls, response: JSONDict) -> "ModelSelection":
        raw = response.get("model_selection")
        raw_dict = dict(raw) if isinstance(raw, dict) else {}
        return cls(
            selected_model=_optional_str(raw_dict.get("selected_model") or response.get("selected_model") or response.get("model_used")),
            selected_decision_path=_optional_str(
                raw_dict.get("selected_decision_path")
                or raw_dict.get("decision_path")
                or response.get("selected_decision_path")
                or response.get("decision_path")
            ),
            reason=_optional_str(raw_dict.get("reason") or response.get("model_selection_reason")),
            frontier_required=_optional_bool(raw_dict.get("frontier_required")),
            native_possible=_optional_bool(raw_dict.get("native_possible")),
            packet_required=_optional_bool(raw_dict.get("packet_required")),
            review_required=_optional_bool(raw_dict.get("review_required")),
            raw=raw_dict,
        )

    from_response = from_backend_response

    def to_dict(self) -> JSONDict:
        return {
            "selected_model": self.selected_model,
            "selected_decision_path": self.selected_decision_path,
            "reason": self.reason,
            "frontier_required": self.frontier_required,
            "native_possible": self.native_possible,
            "packet_required": self.packet_required,
            "review_required": self.review_required,
        }


@dataclass
class DecisionBrief:
    """Small, stable view of a decision for agents and product code.

    ``Decision`` keeps the full normalized object and raw backend payload for
    advanced users. ``DecisionBrief`` is the polished surface: enough to choose
    the next step without learning every historical response shape.
    """

    request_id: Optional[str]
    proposed_action: Optional[str]
    recommended_action: Optional[str]
    recommendation: Optional[str]
    mode: Optional[str]
    can_run: bool
    needs_review: bool
    needs_more_context: bool
    should_not_run: bool
    risk: Optional[float] = None
    confidence: Optional[float] = None
    expected_regret: Optional[float] = None
    reason: Optional[str] = None
    system: Optional[str] = None
    selected_model: Optional[str] = None
    decision_path: Optional[str] = None
    world_state_used: Optional[bool] = None
    verification_steps: int = 0
    obligations: int = 0
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> JSONDict:
        return {
            "request_id": self.request_id,
            "proposed_action": self.proposed_action,
            "recommended_action": self.recommended_action,
            "recommendation": self.recommendation,
            "mode": self.mode,
            "can_run": self.can_run,
            "needs_review": self.needs_review,
            "needs_more_context": self.needs_more_context,
            "should_not_run": self.should_not_run,
            "risk": self.risk,
            "confidence": self.confidence,
            "expected_regret": self.expected_regret,
            "reason": self.reason,
            "system": self.system,
            "selected_model": self.selected_model,
            "decision_path": self.decision_path,
            "world_state_used": self.world_state_used,
            "verification_steps": self.verification_steps,
            "obligations": self.obligations,
            "warnings": self.warnings,
        }


@dataclass
class Decision:
    """The central SDK object: a better decision for a proposed IT agent action."""

    id: Optional[str]
    request_id: Optional[str]
    proposed_action: Optional[str]
    better_action: Optional[str]
    selected_model: Optional[str]
    model_selection_reason: Optional[str]
    decision_path: Optional[str]
    packet: DecisionPacket
    brain: DecisionBrainResult
    mode: Optional[str]
    can_run: bool
    needs_review: bool
    needs_more_context: bool
    should_not_run: bool
    risk: Optional[float]
    confidence: Optional[float]
    expected_regret: Optional[float]
    verification_plan: list[Any] = field(default_factory=list)
    obligations: list[Any] = field(default_factory=list)
    learning_hooks: list[Any] = field(default_factory=list)
    model_selection: ModelSelection = field(default_factory=ModelSelection)
    raw: JSONDict = field(default_factory=dict)
    _reviews: Any = field(default=None, repr=False, compare=False)
    _outcomes: Any = field(default=None, repr=False, compare=False)

    @classmethod
    def from_backend_response(
        cls,
        raw: JSONDict,
        *,
        client: Any = None,
        reviews: Any = None,
        outcomes: Any = None,
        proposed_action: Optional[str] = None,
        context: Optional[JSONDict] = None,
    ) -> "Decision":
        attached_reviews = reviews if reviews is not None else getattr(client, "reviews", None)
        attached_outcomes = outcomes if outcomes is not None else getattr(client, "outcomes", None)

        packet_payload = raw.get("decision_packet") if isinstance(raw.get("decision_packet"), dict) else None
        packet = DecisionPacket.from_payload(packet_payload, proposed_action=proposed_action or "", context=context)
        brain = DecisionBrainResult.from_response(raw)
        model_selection = ModelSelection.from_backend_response(raw)

        request_id = _optional_str(raw.get("request_id") or raw.get("validation_id") or raw.get("id"))
        resolved_proposed_action = _optional_str(
            proposed_action
            or raw.get("proposed_action")
            or raw.get("action")
            or _nested(raw, "decision_runtime_spine", "decision", "action")
        )
        better_action = _extract_better_action(raw)
        mode = _derive_mode(raw)
        can_run, needs_review, needs_more_context, should_not_run = _derive_flags(raw, mode)

        confidence = _first_float(
            raw.get("confidence"),
            _nested(raw, "intelligence", "confidence", "score"),
            _nested(raw, "decision_packet", "context", "confidence", "score"),
            brain.confidence,
        )
        expected_regret = _first_float(
            raw.get("expected_regret"),
            _nested(raw, "decision_intelligence", "projected_regret"),
            _nested(raw, "decision_runtime_spine", "decision", "projected_regret"),
            brain.expected_regret,
        )

        return cls(
            id=request_id,
            request_id=request_id,
            proposed_action=resolved_proposed_action,
            better_action=better_action,
            selected_model=model_selection.selected_model,
            model_selection_reason=model_selection.reason,
            decision_path=model_selection.selected_decision_path,
            packet=packet,
            brain=brain,
            mode=mode,
            can_run=can_run,
            needs_review=needs_review,
            needs_more_context=needs_more_context,
            should_not_run=should_not_run,
            risk=_first_float(raw.get("risk"), raw.get("risk_score"), _nested(raw, "decision_runtime_spine", "decision", "risk_score")),
            confidence=confidence,
            expected_regret=expected_regret,
            verification_plan=list(packet.verification_plan or _as_list(raw.get("verification_plan"))),
            obligations=list(packet.obligations or _as_list(raw.get("open_obligations") or raw.get("obligations"))),
            learning_hooks=list(packet.learning_hooks or _as_list(raw.get("learning_hooks"))),
            model_selection=model_selection,
            raw=raw,
            _reviews=attached_reviews,
            _outcomes=attached_outcomes,
        )

    @property
    def reason(self) -> Optional[str]:
        """Human-facing rationale line when the backend supplied one.

        Prefer top-level advisory ``reason`` from the evaluate response, then brain
        review/reasoning fields, then model-selection rationale. Empty strings are
        treated as absent."""
        primary = _optional_str(self.raw.get("reason"))
        if primary:
            return primary
        if self.brain.review_reason:
            rr = _optional_str(self.brain.review_reason)
            if rr:
                return rr
        if self.brain.reasoning_summary:
            return _optional_str(self.brain.reasoning_summary)
        return _optional_str(self.model_selection_reason)

    @classmethod
    def from_response(
        cls,
        response: JSONDict,
        *,
        proposed_action: Optional[str] = None,
        context: Optional[JSONDict] = None,
        requested_model_selection: str = "auto",
        reviews: Any = None,
        outcomes: Any = None,
    ) -> "Decision":
        return cls.from_backend_response(
            response,
            proposed_action=proposed_action,
            context=context,
            reviews=reviews,
            outcomes=outcomes,
        )

    def request_review(self, *, reason: Optional[str] = None, modified_action: Optional[str] = None, better_action: Optional[str] = None) -> JSONDict:
        if self._reviews is None:
            raise RuntimeError("This Decision is not attached to a BIGHUB client; call bighub.reviews.create_from_decision(decision) instead.")
        return self._reviews.create_from_decision(self, reason=reason, modified_action=modified_action or better_action)

    def report_outcome(
        self,
        *,
        status: str,
        evidence: Optional[JSONDict] = None,
        description: str = "",
        **kwargs: Any,
    ) -> JSONDict:
        if self._outcomes is None:
            raise RuntimeError("This Decision is not attached to a BIGHUB client; call bighub.outcomes.report(...) instead.")
        details = dict(evidence or {})
        decision_snapshot = kwargs.pop("decision_snapshot", self.to_dict())
        return self._outcomes.report(
            request_id=self.request_id,
            status=status,
            description=description,
            details=details or None,
            production_action=self.proposed_action or "",
            human_final_action=self.better_action or "",
            outcome_label_quality="sdk",
            decision_snapshot=decision_snapshot,
            **kwargs,
        )

    def to_dict(self) -> JSONDict:
        return {
            "id": self.id,
            "request_id": self.request_id,
            "proposed_action": self.proposed_action,
            "better_action": self.better_action,
            "selected_model": self.selected_model,
            "model_selection_reason": self.model_selection_reason,
            "decision_path": self.decision_path,
            "packet": self.packet.to_dict(),
            "brain": self.brain.to_dict(),
            "mode": self.mode,
            "can_run": self.can_run,
            "needs_review": self.needs_review,
            "needs_more_context": self.needs_more_context,
            "should_not_run": self.should_not_run,
            "risk": self.risk,
            "confidence": self.confidence,
            "expected_regret": self.expected_regret,
            "verification_plan": self.verification_plan,
            "obligations": self.obligations,
            "learning_hooks": self.learning_hooks,
            "model_selection": self.model_selection.to_dict(),
        }

    def brief(self) -> DecisionBrief:
        """Return the polished decision surface most callers should consume."""

        warnings = self.raw.get("warnings")
        if not isinstance(warnings, list):
            warnings = []
        return DecisionBrief(
            request_id=self.request_id,
            proposed_action=self.proposed_action,
            recommended_action=self.better_action or self.proposed_action,
            recommendation=self.brain.recommendation or _optional_str(self.raw.get("recommendation") or self.raw.get("result")),
            mode=self.mode,
            can_run=self.can_run,
            needs_review=self.needs_review,
            needs_more_context=self.needs_more_context,
            should_not_run=self.should_not_run,
            risk=self.risk,
            confidence=self.confidence,
            expected_regret=self.expected_regret,
            reason=self.reason,
            system=self.packet.system or _optional_str(self.raw.get("domain")),
            selected_model=self.selected_model,
            decision_path=self.decision_path,
            world_state_used=self.brain.world_state_used,
            verification_steps=len(self.verification_plan),
            obligations=len(self.obligations),
            warnings=[str(item) for item in warnings if item not in (None, "")],
        )

    summary = brief

    def to_brief_dict(self) -> JSONDict:
        """Dictionary form of :meth:`brief` for JSON logs and MCP adapters."""

        return self.brief().to_dict()


@dataclass
class AsyncDecision(Decision):
    """Decision returned by ``AsyncBighubClient`` with real async helpers."""

    async def request_review(self, *, reason: Optional[str] = None, modified_action: Optional[str] = None, better_action: Optional[str] = None) -> JSONDict:  # type: ignore[override]
        if self._reviews is None:
            raise RuntimeError("This Decision is not attached to an async BIGHUB client; call await bighub.reviews.create_from_decision(decision) instead.")
        return await self._reviews.create_from_decision(self, reason=reason, modified_action=modified_action or better_action)

    async def report_outcome(
        self,
        *,
        status: str,
        evidence: Optional[JSONDict] = None,
        description: str = "",
        **kwargs: Any,
    ) -> JSONDict:
        if self._outcomes is None:
            raise RuntimeError("This Decision is not attached to an async BIGHUB client; call await bighub.outcomes.report(...) instead.")
        details = dict(evidence or {})
        decision_snapshot = kwargs.pop("decision_snapshot", self.to_dict())
        return await self._outcomes.report(
            request_id=self.request_id,
            status=status,
            description=description,
            details=details or None,
            production_action=self.proposed_action or "",
            human_final_action=self.better_action or "",
            outcome_label_quality="sdk",
            decision_snapshot=decision_snapshot,
            **kwargs,
        )


class BackendDecisionNormalizer:
    """Central backend ``/actions/evaluate`` -> SDK Decision normalizer."""

    @staticmethod
    def normalize(raw: JSONDict, *, client: Any = None, proposed_action: Optional[str] = None, context: Optional[JSONDict] = None) -> Decision:
        return Decision.from_backend_response(raw, client=client, proposed_action=proposed_action, context=context)


def _extract_better_action(raw: JSONDict) -> Optional[str]:
    direct = (
        raw.get("better_action")
        or raw.get("recommended_action")
        or _nested(raw, "decision_packet", "better_action")
        or _nested(raw, "decision_packet", "action_contract", "better_action")
    )
    if direct:
        return str(direct)
    alternatives = _nested(raw, "decision_intelligence", "alternatives")
    if isinstance(alternatives, list) and alternatives:
        first = alternatives[0]
        if isinstance(first, dict):
            return _optional_str(first.get("better_action") or first.get("action"))
        return _optional_str(first)
    packet_alternatives = _nested(raw, "decision_packet", "alternatives")
    if isinstance(packet_alternatives, list) and packet_alternatives:
        first = packet_alternatives[0]
        if isinstance(first, dict):
            return _optional_str(first.get("action"))
        return _optional_str(first)
    return None


def _derive_mode(raw: JSONDict) -> Optional[str]:
    recommendation = str(raw.get("recommendation") or "").lower()
    result = str(raw.get("result") or "").lower()
    explicit = str(raw.get("execution_mode") or raw.get("mode") or "").strip().lower()

    if raw.get("dry_run") is True:
        return "dry_run"
    if raw.get("needs_more_context") is True or raw.get("request_type") in {"clarification_needed", "needs_more_context"}:
        return "needs_context"
    if raw.get("human_review") is True or raw.get("requires_approval") is True or result == "requires_approval" or recommendation == "review_recommended":
        return "review"
    if explicit in MODES:
        return explicit
    if explicit in {"full", "allowed"}:
        return "autonomous"
    if explicit in {"limited", "restricted", "conditional"}:
        return "constrained"
    if explicit in {"denied", "blocked", "review_required"}:
        return "blocked" if explicit != "review_required" else "review"
    if recommendation == "do_not_proceed" or result in {"blocked", "denied"} or raw.get("allowed") is False:
        return "blocked"
    if recommendation == "proceed_with_caution" or result == "limited":
        return "constrained"
    if recommendation == "proceed" or result == "allowed" or raw.get("allowed") is True:
        return "autonomous"
    return None


def _derive_flags(raw: JSONDict, mode: Optional[str]) -> tuple[bool, bool, bool, bool]:
    needs_review = bool(mode == "review")
    needs_more_context = bool(mode == "needs_context")
    should_not_run = bool(mode == "blocked")
    can_run = bool(mode in {"autonomous", "constrained"} and not needs_review and not should_not_run)
    return can_run, needs_review, needs_more_context, should_not_run


def _optional_str(value: Any) -> Optional[str]:
    if value in (None, ""):
        return None
    return str(value)


def _optional_bool(value: Any) -> Optional[bool]:
    if value is None:
        return None
    return bool(value)


def _first_float(*values: Any) -> Optional[float]:
    for value in values:
        if value in (None, ""):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _nested(data: JSONDict, *path: str) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current
