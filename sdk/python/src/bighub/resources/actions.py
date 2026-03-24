from __future__ import annotations

from typing import Any, Dict, List, Optional, overload

from ..models import ActionSubmitPayloadModel, to_payload
from ..protocols import AsyncTransportProtocol, SyncTransportProtocol
from ..types import (
    ActionEvaluateResponse,
    ActionSubmitRequest,
    ActionSubmitResponse,
    ActionSubmitPayloadRequest,
    DashboardSummaryResponse,
    DecisionMemoryEvent,
    JSONDict,
    LiveConnectionResponse,
    MemoryContextResponse,
    MemoryIngestResponse,
    MemoryRecommendationsResponse,
    MemoryRefreshResponse,
    ObserverStatsResponse,
    ValidationVerifyResponse,
    ValueProtectedHistoryResponse,
)


def _merge_context(
    *,
    context: Optional[JSONDict],
    metadata: Optional[JSONDict],
) -> Optional[JSONDict]:
    out: Dict[str, Any] = {}
    if isinstance(metadata, dict):
        out.update(metadata)
    if isinstance(context, dict):
        out.update(context)
    return out or None


def _normalize_action_payload(payload: JSONDict) -> JSONDict:
    out = dict(payload)
    ctx = _merge_context(
        context=out.get("context") if isinstance(out.get("context"), dict) else None,
        metadata=out.get("metadata") if isinstance(out.get("metadata"), dict) else None,
    )
    out.pop("metadata", None)
    if ctx is not None:
        out["context"] = ctx
    return out


class ActionsAPI:
    """Sync API for action evaluation and decision intelligence endpoints."""

    def __init__(self, transport: SyncTransportProtocol) -> None:
        self._transport = transport

    def evaluate(
        self,
        *,
        action: str,
        value: Optional[float] = None,
        target: Optional[str] = None,
        actor: str = "AI_AGENT",
        domain: Optional[str] = None,
        context: Optional[JSONDict] = None,
        metadata: Optional[JSONDict] = None,
        idempotency_key: Optional[str] = None,
    ) -> ActionEvaluateResponse:
        """Evaluate an action via ``POST /actions/evaluate``.

        Returns a structured recommendation with decision intelligence,
        trajectory health, alternatives, and evidence quality — not just
        an allow/block verdict.

        Primary response fields::

            recommendation          proceed | proceed_with_caution
                                    | review_recommended | do_not_proceed
            recommendation_confidence   high | medium | low
            risk_score              0.0 – 1.0
            decision_intelligence   projected_regret, trajectory_health,
                                    alternatives, evidence_status, rationale
            enforcement_mode        advisory | review | enforced
        """
        payload: ActionSubmitRequest = {"action": action, "actor": actor}
        if value is not None:
            payload["value"] = value
        if target is not None:
            payload["target"] = target
        if domain is not None:
            payload["domain"] = domain
        merged_context = _merge_context(context=context, metadata=metadata)
        if merged_context:
            payload["context"] = merged_context
        return self._transport.request(
            method="POST",
            path="/actions/evaluate",
            json_body=_normalize_action_payload(payload),
            idempotency_key=idempotency_key,
        )

    submit = evaluate

    @overload
    def evaluate_payload(self, *, payload: ActionSubmitPayloadRequest, idempotency_key: Optional[str] = None) -> ActionEvaluateResponse:
        ...

    @overload
    def evaluate_payload(self, *, payload: ActionSubmitPayloadModel, idempotency_key: Optional[str] = None) -> ActionEvaluateResponse:
        ...

    def evaluate_payload(
        self,
        *,
        payload: ActionSubmitPayloadRequest | ActionSubmitPayloadModel,
        idempotency_key: Optional[str] = None,
    ) -> ActionEvaluateResponse:
        """Evaluate with full decision intelligence payload via ``POST /actions/evaluate``.

        Identical endpoint to :meth:`evaluate` but accepts a free-form
        payload dict or :class:`ActionSubmitPayloadModel` for maximum flexibility.
        """
        return self._transport.request(
            method="POST",
            path="/actions/evaluate",
            json_body=_normalize_action_payload(to_payload(payload)),
            idempotency_key=idempotency_key,
        )

    submit_payload = evaluate_payload

    @overload
    def dry_run(self, *, payload: ActionSubmitPayloadRequest, idempotency_key: Optional[str] = None) -> ActionEvaluateResponse:
        ...

    @overload
    def dry_run(self, *, payload: ActionSubmitPayloadModel, idempotency_key: Optional[str] = None) -> ActionEvaluateResponse:
        ...

    def dry_run(
        self,
        *,
        payload: ActionSubmitPayloadRequest | ActionSubmitPayloadModel,
        idempotency_key: Optional[str] = None,
    ) -> ActionEvaluateResponse:
        """Non-persistent evaluation via ``POST /actions/evaluate`` with ``dry_run=true``."""
        normalized = _normalize_action_payload(to_payload(payload))
        return self._transport.request(
            method="POST",
            path="/actions/evaluate",
            json_body={**normalized, "dry_run": True},
            idempotency_key=idempotency_key,
        )

    def evaluate_batch(
        self,
        *,
        actions: List[JSONDict],
        domain: Optional[str] = None,
        actor: str = "AI_AGENT",
    ) -> List[ActionEvaluateResponse]:
        """Evaluate multiple actions in a single request via ``POST /actions/evaluate/batch``."""
        payload: JSONDict = {"actions": actions, "actor": actor}
        if domain is not None:
            payload["domain"] = domain
        return self._transport.request(
            method="POST",
            path="/actions/evaluate/batch",
            json_body=payload,
        )

    def value_protected_history(
        self,
        *,
        days: int = 30,
    ) -> ValueProtectedHistoryResponse:
        """Get value-protected history over time via ``GET /actions/dashboard/value-protected-history``."""
        return self._transport.request(
            method="GET",
            path="/actions/dashboard/value-protected-history",
            params={"days": days},
        )

    def connect(
        self,
        *,
        actor: str = "AI_AGENT",
        context: Optional[JSONDict] = None,
    ) -> LiveConnectionResponse:
        """Open a live connection slot via ``/actions/live/connect``."""
        return self._transport.request(
            method="POST",
            path="/actions/live/connect",
            json_body={"actor": actor, "context": context or {}},
        )

    def heartbeat(
        self,
        *,
        connection_id: str,
        context: Optional[JSONDict] = None,
    ) -> LiveConnectionResponse:
        """Heartbeat a live connection via ``/actions/live/heartbeat``."""
        return self._transport.request(
            method="POST",
            path="/actions/live/heartbeat",
            json_body={"connection_id": connection_id, "context": context or {}},
        )

    def disconnect(
        self,
        *,
        connection_id: str,
        context: Optional[JSONDict] = None,
    ) -> JSONDict:
        """Disconnect a live connection via ``/actions/live/disconnect``."""
        return self._transport.request(
            method="POST",
            path="/actions/live/disconnect",
            json_body={"connection_id": connection_id, "context": context or {}},
        )

    def begin_live_session(
        self,
        *,
        actor: str = "AI_AGENT",
        context: Optional[JSONDict] = None,
    ) -> "LiveActionsSession":
        """Create a managed live session (connect + auto connection_id propagation)."""
        connected = self.connect(actor=actor, context=context or {})
        connection_id = str(connected["connection_id"])
        base_context = dict(context or {})
        return LiveActionsSession(
            api=self,
            actor=actor,
            connection_id=connection_id,
            base_context=base_context,
        )

    def verify_validation(self, validation_id: str) -> ValidationVerifyResponse:
        return self._transport.request(
            method="GET",
            path=f"/actions/validations/{validation_id}/verify",
        )

    def observer_stats(self) -> ObserverStatsResponse:
        return self._transport.request(method="GET", path="/actions/observer/stats")

    def dashboard_summary(self) -> DashboardSummaryResponse:
        return self._transport.request(method="GET", path="/actions/dashboard/summary")

    def status(self) -> JSONDict:
        return self._transport.request(method="GET", path="/actions/status")

    def ingest_memory(
        self,
        *,
        events: list[DecisionMemoryEvent],
        source: str = "adapter",
        source_version: Optional[str] = None,
        actor: Optional[str] = None,
        domain: Optional[str] = None,
        model: Optional[str] = None,
        trace_id: Optional[str] = None,
        redact: bool = True,
        redaction_policy: str = "default",
    ) -> MemoryIngestResponse:
        payload: JSONDict = {"source": source, "events": events}
        payload["redact"] = redact
        payload["redaction_policy"] = redaction_policy
        if source_version is not None:
            payload["source_version"] = source_version
        if actor is not None:
            payload["actor"] = actor
        if domain is not None:
            payload["domain"] = domain
        if model is not None:
            payload["model"] = model
        if trace_id is not None:
            payload["trace_id"] = trace_id
        return self._transport.request(
            method="POST",
            path="/actions/memory/ingest",
            json_body=payload,
        )

    def memory_context(
        self,
        *,
        window_hours: int = 24,
        tool: Optional[str] = None,
        domain: Optional[str] = None,
        actor: Optional[str] = None,
        source: Optional[str] = None,
        limit_recent: int = 25,
    ) -> MemoryContextResponse:
        params: JSONDict = {"window_hours": window_hours, "limit_recent": limit_recent}
        if tool is not None:
            params["tool"] = tool
        if domain is not None:
            params["domain"] = domain
        if actor is not None:
            params["actor"] = actor
        if source is not None:
            params["source"] = source
        return self._transport.request(
            method="GET",
            path="/actions/memory/context",
            params=params,
        )

    def refresh_memory_aggregates(self, *, concurrent: bool = False, window_hours: int = 24) -> MemoryRefreshResponse:
        return self._transport.request(
            method="POST",
            path="/actions/memory/refresh-aggregates",
            params={"concurrent": concurrent, "window_hours": window_hours},
        )

    def memory_recommendations(
        self,
        *,
        window_hours: int = 24,
        scope: Optional[JSONDict] = None,
        tool: Optional[str] = None,
        domain: Optional[str] = None,
        actor: Optional[str] = None,
        source: Optional[str] = None,
        min_events: int = 20,
        min_blocked_rate: float = 0.15,
        min_approval_rate: float = 0.10,
        min_tool_error_rate: float = 0.05,
        limit_recommendations: int = 10,
        include_examples: bool = True,
        auto_apply: bool = False,
    ) -> MemoryRecommendationsResponse:
        payload: JSONDict = {
            "window_hours": window_hours,
            "min_events": min_events,
            "min_blocked_rate": min_blocked_rate,
            "min_approval_rate": min_approval_rate,
            "min_tool_error_rate": min_tool_error_rate,
            "limit_recommendations": limit_recommendations,
            "include_examples": include_examples,
            "auto_apply": auto_apply,
        }
        if scope is not None:
            payload["scope"] = scope
        if tool is not None:
            payload["tool"] = tool
        if domain is not None:
            payload["domain"] = domain
        if actor is not None:
            payload["actor"] = actor
        if source is not None:
            payload["source"] = source
        return self._transport.request(
            method="POST",
            path="/actions/memory/recommendations",
            json_body=payload,
        )


class AsyncActionsAPI:
    """Async API for action evaluation and decision intelligence endpoints."""

    def __init__(self, transport: AsyncTransportProtocol) -> None:
        self._transport = transport

    async def evaluate(
        self,
        *,
        action: str,
        value: Optional[float] = None,
        target: Optional[str] = None,
        actor: str = "AI_AGENT",
        domain: Optional[str] = None,
        context: Optional[JSONDict] = None,
        metadata: Optional[JSONDict] = None,
        idempotency_key: Optional[str] = None,
    ) -> ActionEvaluateResponse:
        """Evaluate an action via ``POST /actions/evaluate``.

        Returns a structured recommendation with decision intelligence,
        trajectory health, alternatives, and evidence quality — not just
        an allow/block verdict.
        """
        payload: ActionSubmitRequest = {"action": action, "actor": actor}
        if value is not None:
            payload["value"] = value
        if target is not None:
            payload["target"] = target
        if domain is not None:
            payload["domain"] = domain
        merged_context = _merge_context(context=context, metadata=metadata)
        if merged_context:
            payload["context"] = merged_context
        return await self._transport.request(
            method="POST",
            path="/actions/evaluate",
            json_body=_normalize_action_payload(payload),
            idempotency_key=idempotency_key,
        )

    submit = evaluate

    @overload
    async def evaluate_payload(self, *, payload: ActionSubmitPayloadRequest, idempotency_key: Optional[str] = None) -> ActionEvaluateResponse:
        ...

    @overload
    async def evaluate_payload(self, *, payload: ActionSubmitPayloadModel, idempotency_key: Optional[str] = None) -> ActionEvaluateResponse:
        ...

    async def evaluate_payload(
        self,
        *,
        payload: ActionSubmitPayloadRequest | ActionSubmitPayloadModel,
        idempotency_key: Optional[str] = None,
    ) -> ActionEvaluateResponse:
        """Evaluate with full decision intelligence payload via ``POST /actions/evaluate``."""
        return await self._transport.request(
            method="POST",
            path="/actions/evaluate",
            json_body=_normalize_action_payload(to_payload(payload)),
            idempotency_key=idempotency_key,
        )

    submit_payload = evaluate_payload

    @overload
    async def dry_run(self, *, payload: ActionSubmitPayloadRequest, idempotency_key: Optional[str] = None) -> ActionEvaluateResponse:
        ...

    @overload
    async def dry_run(self, *, payload: ActionSubmitPayloadModel, idempotency_key: Optional[str] = None) -> ActionEvaluateResponse:
        ...

    async def dry_run(
        self,
        *,
        payload: ActionSubmitPayloadRequest | ActionSubmitPayloadModel,
        idempotency_key: Optional[str] = None,
    ) -> ActionEvaluateResponse:
        """Non-persistent evaluation via ``POST /actions/evaluate`` with ``dry_run=true``."""
        normalized = _normalize_action_payload(to_payload(payload))
        return await self._transport.request(
            method="POST",
            path="/actions/evaluate",
            json_body={**normalized, "dry_run": True},
            idempotency_key=idempotency_key,
        )

    async def evaluate_batch(
        self,
        *,
        actions: List[JSONDict],
        domain: Optional[str] = None,
        actor: str = "AI_AGENT",
    ) -> List[ActionEvaluateResponse]:
        """Evaluate multiple actions in a single request via ``POST /actions/evaluate/batch``."""
        payload: JSONDict = {"actions": actions, "actor": actor}
        if domain is not None:
            payload["domain"] = domain
        return await self._transport.request(
            method="POST",
            path="/actions/evaluate/batch",
            json_body=payload,
        )

    async def value_protected_history(
        self,
        *,
        days: int = 30,
    ) -> ValueProtectedHistoryResponse:
        """Get value-protected history over time via ``GET /actions/dashboard/value-protected-history``."""
        return await self._transport.request(
            method="GET",
            path="/actions/dashboard/value-protected-history",
            params={"days": days},
        )

    async def connect(
        self,
        *,
        actor: str = "AI_AGENT",
        context: Optional[JSONDict] = None,
    ) -> LiveConnectionResponse:
        """Open a live connection slot via ``/actions/live/connect``."""
        return await self._transport.request(
            method="POST",
            path="/actions/live/connect",
            json_body={"actor": actor, "context": context or {}},
        )

    async def heartbeat(
        self,
        *,
        connection_id: str,
        context: Optional[JSONDict] = None,
    ) -> LiveConnectionResponse:
        """Heartbeat a live connection via ``/actions/live/heartbeat``."""
        return await self._transport.request(
            method="POST",
            path="/actions/live/heartbeat",
            json_body={"connection_id": connection_id, "context": context or {}},
        )

    async def disconnect(
        self,
        *,
        connection_id: str,
        context: Optional[JSONDict] = None,
    ) -> JSONDict:
        """Disconnect a live connection via ``/actions/live/disconnect``."""
        return await self._transport.request(
            method="POST",
            path="/actions/live/disconnect",
            json_body={"connection_id": connection_id, "context": context or {}},
        )

    async def begin_live_session(
        self,
        *,
        actor: str = "AI_AGENT",
        context: Optional[JSONDict] = None,
    ) -> "AsyncLiveActionsSession":
        """Create a managed live session (connect + auto connection_id propagation)."""
        connected = await self.connect(actor=actor, context=context or {})
        connection_id = str(connected["connection_id"])
        base_context = dict(context or {})
        return AsyncLiveActionsSession(
            api=self,
            actor=actor,
            connection_id=connection_id,
            base_context=base_context,
        )

    async def verify_validation(self, validation_id: str) -> ValidationVerifyResponse:
        return await self._transport.request(
            method="GET",
            path=f"/actions/validations/{validation_id}/verify",
        )

    async def observer_stats(self) -> ObserverStatsResponse:
        return await self._transport.request(method="GET", path="/actions/observer/stats")

    async def dashboard_summary(self) -> DashboardSummaryResponse:
        return await self._transport.request(method="GET", path="/actions/dashboard/summary")

    async def status(self) -> JSONDict:
        return await self._transport.request(method="GET", path="/actions/status")

    async def ingest_memory(
        self,
        *,
        events: list[DecisionMemoryEvent],
        source: str = "adapter",
        source_version: Optional[str] = None,
        actor: Optional[str] = None,
        domain: Optional[str] = None,
        model: Optional[str] = None,
        trace_id: Optional[str] = None,
        redact: bool = True,
        redaction_policy: str = "default",
    ) -> MemoryIngestResponse:
        payload: JSONDict = {"source": source, "events": events}
        payload["redact"] = redact
        payload["redaction_policy"] = redaction_policy
        if source_version is not None:
            payload["source_version"] = source_version
        if actor is not None:
            payload["actor"] = actor
        if domain is not None:
            payload["domain"] = domain
        if model is not None:
            payload["model"] = model
        if trace_id is not None:
            payload["trace_id"] = trace_id
        return await self._transport.request(
            method="POST",
            path="/actions/memory/ingest",
            json_body=payload,
        )

    async def memory_context(
        self,
        *,
        window_hours: int = 24,
        tool: Optional[str] = None,
        domain: Optional[str] = None,
        actor: Optional[str] = None,
        source: Optional[str] = None,
        limit_recent: int = 25,
    ) -> MemoryContextResponse:
        params: JSONDict = {"window_hours": window_hours, "limit_recent": limit_recent}
        if tool is not None:
            params["tool"] = tool
        if domain is not None:
            params["domain"] = domain
        if actor is not None:
            params["actor"] = actor
        if source is not None:
            params["source"] = source
        return await self._transport.request(
            method="GET",
            path="/actions/memory/context",
            params=params,
        )

    async def refresh_memory_aggregates(self, *, concurrent: bool = False, window_hours: int = 24) -> MemoryRefreshResponse:
        return await self._transport.request(
            method="POST",
            path="/actions/memory/refresh-aggregates",
            params={"concurrent": concurrent, "window_hours": window_hours},
        )

    async def memory_recommendations(
        self,
        *,
        window_hours: int = 24,
        scope: Optional[JSONDict] = None,
        tool: Optional[str] = None,
        domain: Optional[str] = None,
        actor: Optional[str] = None,
        source: Optional[str] = None,
        min_events: int = 20,
        min_blocked_rate: float = 0.15,
        min_approval_rate: float = 0.10,
        min_tool_error_rate: float = 0.05,
        limit_recommendations: int = 10,
        include_examples: bool = True,
        auto_apply: bool = False,
    ) -> MemoryRecommendationsResponse:
        payload: JSONDict = {
            "window_hours": window_hours,
            "min_events": min_events,
            "min_blocked_rate": min_blocked_rate,
            "min_approval_rate": min_approval_rate,
            "min_tool_error_rate": min_tool_error_rate,
            "limit_recommendations": limit_recommendations,
            "include_examples": include_examples,
            "auto_apply": auto_apply,
        }
        if scope is not None:
            payload["scope"] = scope
        if tool is not None:
            payload["tool"] = tool
        if domain is not None:
            payload["domain"] = domain
        if actor is not None:
            payload["actor"] = actor
        if source is not None:
            payload["source"] = source
        return await self._transport.request(
            method="POST",
            path="/actions/memory/recommendations",
            json_body=payload,
        )


class LiveActionsSession:
    """Managed sync live connection session for actions APIs."""

    def __init__(
        self,
        *,
        api: ActionsAPI,
        actor: str,
        connection_id: str,
        base_context: Optional[JSONDict] = None,
    ) -> None:
        self._api = api
        self.actor = actor
        self.connection_id = connection_id
        self._base_context = dict(base_context or {})

    def _live_context(self, context: Optional[JSONDict] = None) -> JSONDict:
        merged = dict(self._base_context)
        if context:
            merged.update(context)
        merged["connection_mode"] = "live"
        merged["require_live_connection"] = True
        merged["connection_id"] = self.connection_id
        return merged

    def evaluate(self, *, action: str, value: Optional[float] = None, target: Optional[str] = None, domain: Optional[str] = None, context: Optional[JSONDict] = None, idempotency_key: Optional[str] = None) -> ActionEvaluateResponse:
        return self._api.evaluate(
            action=action,
            value=value,
            target=target,
            actor=self.actor,
            domain=domain,
            context=self._live_context(context),
            idempotency_key=idempotency_key,
        )

    submit = evaluate

    def heartbeat(self, *, context: Optional[JSONDict] = None) -> JSONDict:
        return self._api.heartbeat(connection_id=self.connection_id, context=context)

    def disconnect(self, *, context: Optional[JSONDict] = None) -> JSONDict:
        return self._api.disconnect(connection_id=self.connection_id, context=context)


class AsyncLiveActionsSession:
    """Managed async live connection session for actions APIs."""

    def __init__(
        self,
        *,
        api: AsyncActionsAPI,
        actor: str,
        connection_id: str,
        base_context: Optional[JSONDict] = None,
    ) -> None:
        self._api = api
        self.actor = actor
        self.connection_id = connection_id
        self._base_context = dict(base_context or {})

    def _live_context(self, context: Optional[JSONDict] = None) -> JSONDict:
        merged = dict(self._base_context)
        if context:
            merged.update(context)
        merged["connection_mode"] = "live"
        merged["require_live_connection"] = True
        merged["connection_id"] = self.connection_id
        return merged

    async def evaluate(self, *, action: str, value: Optional[float] = None, target: Optional[str] = None, domain: Optional[str] = None, context: Optional[JSONDict] = None, idempotency_key: Optional[str] = None) -> ActionEvaluateResponse:
        return await self._api.evaluate(
            action=action,
            value=value,
            target=target,
            actor=self.actor,
            domain=domain,
            context=self._live_context(context),
            idempotency_key=idempotency_key,
        )

    submit = evaluate

    async def heartbeat(self, *, context: Optional[JSONDict] = None) -> JSONDict:
        return await self._api.heartbeat(connection_id=self.connection_id, context=context)

    async def disconnect(self, *, context: Optional[JSONDict] = None) -> JSONDict:
        return await self._api.disconnect(connection_id=self.connection_id, context=context)
