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
    salient_factors: list[str] = field(default_factory=list)
    action_space_counts: dict[str, int] = field(default_factory=dict)
    action_family: Optional[str] = None
    interpreted_action: Optional[str] = None
    intent_mismatch: Optional[bool] = None
    signal_confidence_floor: Optional[float] = None
    conflicted_signal_count: int = 0
    high_spoofability_signal_count: int = 0
    signal_manipulation_risk: Optional[str] = None
    signal_manipulation_requires_review: Optional[bool] = None
    signal_manipulation_should_suspend: Optional[bool] = None
    signal_manipulation_controls: list[str] = field(default_factory=list)
    safe_novelty_lane_status: Optional[str] = None
    safe_novelty_lane_mode: Optional[str] = None
    safe_novelty_lane_eligible: Optional[bool] = None
    top_regret_dimensions: list[str] = field(default_factory=list)
    promise_types: list[str] = field(default_factory=list)
    catastrophic_ceiling_active: Optional[bool] = None
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
            "salient_factors": self.salient_factors,
            "action_space_counts": self.action_space_counts,
            "action_family": self.action_family,
            "interpreted_action": self.interpreted_action,
            "intent_mismatch": self.intent_mismatch,
            "signal_confidence_floor": self.signal_confidence_floor,
            "conflicted_signal_count": self.conflicted_signal_count,
            "high_spoofability_signal_count": self.high_spoofability_signal_count,
            "signal_manipulation_risk": self.signal_manipulation_risk,
            "signal_manipulation_requires_review": self.signal_manipulation_requires_review,
            "signal_manipulation_should_suspend": self.signal_manipulation_should_suspend,
            "signal_manipulation_controls": self.signal_manipulation_controls,
            "safe_novelty_lane_status": self.safe_novelty_lane_status,
            "safe_novelty_lane_mode": self.safe_novelty_lane_mode,
            "safe_novelty_lane_eligible": self.safe_novelty_lane_eligible,
            "top_regret_dimensions": self.top_regret_dimensions,
            "promise_types": self.promise_types,
            "catastrophic_ceiling_active": self.catastrophic_ceiling_active,
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
    expected_regret_vector: JSONDict = field(default_factory=dict)
    verification_plan: list[Any] = field(default_factory=list)
    obligations: list[Any] = field(default_factory=list)
    learning_hooks: list[Any] = field(default_factory=list)
    responsible_action_space: JSONDict = field(default_factory=dict)
    salient_factors: list[JSONDict] = field(default_factory=list)
    signal_epistemology: JSONDict = field(default_factory=dict)
    signal_manipulation_audit: JSONDict = field(default_factory=dict)
    operational_intent: JSONDict = field(default_factory=dict)
    agent_operational_body: JSONDict = field(default_factory=dict)
    action_interpretation_layer: JSONDict = field(default_factory=dict)
    safe_novelty_lane: JSONDict = field(default_factory=dict)
    performative_contracts: list[JSONDict] = field(default_factory=list)
    catastrophic_ceiling: JSONDict = field(default_factory=dict)
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
        responsible_action_space = _normalize_action_space(raw.get("responsible_action_space"))
        salient_factors = [dict(item) for item in _as_list(raw.get("salient_factors")) if isinstance(item, dict)]
        signal_epistemology = (
            dict(raw.get("signal_epistemology"))
            if isinstance(raw.get("signal_epistemology"), dict)
            else {}
        )
        signal_manipulation_audit = (
            dict(raw.get("signal_manipulation_audit"))
            if isinstance(raw.get("signal_manipulation_audit"), dict)
            else {}
        )
        operational_intent = dict(raw.get("operational_intent")) if isinstance(raw.get("operational_intent"), dict) else {}
        agent_operational_body = dict(raw.get("agent_operational_body")) if isinstance(raw.get("agent_operational_body"), dict) else {}
        action_interpretation_layer = (
            dict(raw.get("action_interpretation_layer"))
            if isinstance(raw.get("action_interpretation_layer"), dict)
            else {}
        )
        safe_novelty_lane = (
            dict(raw.get("safe_novelty_lane"))
            if isinstance(raw.get("safe_novelty_lane"), dict)
            else {}
        )
        performative_contracts = [
            dict(item)
            for item in _as_list(raw.get("performative_contracts"))
            if isinstance(item, dict)
        ]
        catastrophic_ceiling = (
            dict(raw.get("catastrophic_ceiling"))
            if isinstance(raw.get("catastrophic_ceiling"), dict)
            else {}
        )
        expected_regret_vector = (
            dict(raw.get("expected_regret_vector"))
            if isinstance(raw.get("expected_regret_vector"), dict)
            else {}
        )

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
            expected_regret_vector=expected_regret_vector,
            verification_plan=list(packet.verification_plan or _as_list(raw.get("verification_plan"))),
            obligations=list(packet.obligations or _as_list(raw.get("open_obligations") or raw.get("obligations"))),
            learning_hooks=list(packet.learning_hooks or _as_list(raw.get("learning_hooks"))),
            responsible_action_space=responsible_action_space,
            salient_factors=salient_factors,
            signal_epistemology=signal_epistemology,
            signal_manipulation_audit=signal_manipulation_audit,
            operational_intent=operational_intent,
            agent_operational_body=agent_operational_body,
            action_interpretation_layer=action_interpretation_layer,
            safe_novelty_lane=safe_novelty_lane,
            performative_contracts=performative_contracts,
            catastrophic_ceiling=catastrophic_ceiling,
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
            "expected_regret_vector": self.expected_regret_vector,
            "verification_plan": self.verification_plan,
            "obligations": self.obligations,
            "learning_hooks": self.learning_hooks,
            "responsible_action_space": self.responsible_action_space,
            "salient_factors": self.salient_factors,
            "signal_epistemology": self.signal_epistemology,
            "signal_manipulation_audit": self.signal_manipulation_audit,
            "operational_intent": self.operational_intent,
            "agent_operational_body": self.agent_operational_body,
            "action_interpretation_layer": self.action_interpretation_layer,
            "safe_novelty_lane": self.safe_novelty_lane,
            "performative_contracts": self.performative_contracts,
            "catastrophic_ceiling": self.catastrophic_ceiling,
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
            salient_factors=[
                str(item.get("factor"))
                for item in self.salient_factors
                if isinstance(item, dict) and item.get("factor") not in (None, "")
            ],
            action_space_counts={
                key: len(value) if isinstance(value, list) else 0
                for key, value in self.responsible_action_space.items()
            },
            action_family=_optional_str(self.action_interpretation_layer.get("action_family")),
            interpreted_action=_optional_str(self.action_interpretation_layer.get("interpreted_action")),
            intent_mismatch=_optional_bool(self.operational_intent.get("mismatch")),
            signal_confidence_floor=_first_float(_nested(self.signal_epistemology, "summary", "min_confidence")),
            conflicted_signal_count=int(_first_float(_nested(self.signal_epistemology, "summary", "conflicted_factors"), 0) or 0),
            high_spoofability_signal_count=int(_first_float(_nested(self.signal_epistemology, "summary", "high_spoofability_factors"), 0) or 0),
            signal_manipulation_risk=_optional_str(self.signal_manipulation_audit.get("manipulation_risk")),
            signal_manipulation_requires_review=_optional_bool(self.signal_manipulation_audit.get("requires_review")),
            signal_manipulation_should_suspend=_optional_bool(self.signal_manipulation_audit.get("should_suspend_autonomous_execution")),
            signal_manipulation_controls=[
                str(item)
                for item in _as_list(self.signal_manipulation_audit.get("required_controls"))
                if item not in (None, "")
            ],
            safe_novelty_lane_status=_optional_str(self.safe_novelty_lane.get("status")),
            safe_novelty_lane_mode=_optional_str(self.safe_novelty_lane.get("recommended_intervention_mode")),
            safe_novelty_lane_eligible=_optional_bool(self.safe_novelty_lane.get("eligible")),
            top_regret_dimensions=[
                str(item)
                for item in _as_list(self.expected_regret_vector.get("dominant_dimensions"))
                if item not in (None, "")
            ],
            promise_types=_unique_strings([
                item.get("promise_type")
                for item in self.performative_contracts
                if isinstance(item, dict)
            ]),
            catastrophic_ceiling_active=_optional_bool(self.catastrophic_ceiling.get("active")),
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


def _normalize_action_space(value: Any) -> JSONDict:
    raw = value if isinstance(value, dict) else {}
    return {
        "available": _action_items(raw.get("available")),
        "constrained": _action_items(raw.get("constrained")),
        "forbidden": _action_items(raw.get("forbidden")),
        "information_gathering": _action_items(raw.get("information_gathering")),
    }


def _action_items(value: Any) -> list[JSONDict]:
    return [dict(item) for item in _as_list(value) if isinstance(item, dict)]


def _unique_strings(values: list[Any]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value in (None, ""):
            continue
        item = str(value)
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _nested(data: JSONDict, *path: str) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current
