from __future__ import annotations

from typing import Optional, overload

from ..models import ActionSubmitV2Model, to_payload
from ..protocols import AsyncTransportProtocol, SyncTransportProtocol
from ..types import (
    ActionSubmitRequest,
    ActionSubmitResponse,
    ActionSubmitV2Request,
    DecisionMemoryEvent,
    JSONDict,
)


class ActionsAPI:
    """Sync API for action evaluation and decision learning endpoints."""

    def __init__(self, transport: SyncTransportProtocol) -> None:
        self._transport = transport

    def submit(
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
    ) -> ActionSubmitResponse:
        """Evaluate an action via `/actions/submit`."""
        payload: ActionSubmitRequest = {"action": action, "actor": actor}
        if value is not None:
            payload["value"] = value
        if target is not None:
            payload["target"] = target
        if domain is not None:
            payload["domain"] = domain
        if context is not None:
            payload["context"] = context
        elif metadata is not None:
            payload["context"] = metadata
        return self._transport.request(
            method="POST",
            path="/actions/submit",
            json_body=payload,
            idempotency_key=idempotency_key,
        )

    evaluate = submit

    @overload
    def submit_v2(self, *, payload: ActionSubmitV2Request, idempotency_key: Optional[str] = None) -> JSONDict:
        ...

    @overload
    def submit_v2(self, *, payload: ActionSubmitV2Model, idempotency_key: Optional[str] = None) -> JSONDict:
        ...

    def submit_v2(
        self,
        *,
        payload: ActionSubmitV2Request | ActionSubmitV2Model,
        idempotency_key: Optional[str] = None,
    ) -> JSONDict:
        """Evaluate action via `/actions/submit/v2`."""
        body = to_payload(payload)
        if "context" not in body and "metadata" in body:
            body["context"] = body["metadata"]
        return self._transport.request(
            method="POST",
            path="/actions/submit/v2",
            json_body=body,
            idempotency_key=idempotency_key,
        )

    @overload
    def dry_run(self, *, payload: ActionSubmitV2Request, idempotency_key: Optional[str] = None) -> JSONDict:
        ...

    @overload
    def dry_run(self, *, payload: ActionSubmitV2Model, idempotency_key: Optional[str] = None) -> JSONDict:
        ...

    def dry_run(
        self,
        *,
        payload: ActionSubmitV2Request | ActionSubmitV2Model,
        idempotency_key: Optional[str] = None,
    ) -> JSONDict:
        """Run a non-persistent evaluation via `/actions/submit/dry-run`."""
        body = to_payload(payload)
        if "context" not in body and "metadata" in body:
            body["context"] = body["metadata"]
        return self._transport.request(
            method="POST",
            path="/actions/submit/dry-run",
            json_body=body,
            idempotency_key=idempotency_key,
        )

    def verify_validation(self, validation_id: str) -> JSONDict:
        return self._transport.request(
            method="GET",
            path=f"/actions/validations/{validation_id}/verify",
        )

    def observer_stats(self) -> JSONDict:
        return self._transport.request(method="GET", path="/actions/observer/stats")

    def dashboard_summary(self) -> JSONDict:
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
    ) -> JSONDict:
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
    ) -> JSONDict:
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

    def refresh_memory_aggregates(self, *, concurrent: bool = False, window_hours: int = 24) -> JSONDict:
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
    ) -> JSONDict:
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
    """Async API for action evaluation and decision learning endpoints."""

    def __init__(self, transport: AsyncTransportProtocol) -> None:
        self._transport = transport

    async def submit(
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
    ) -> ActionSubmitResponse:
        """Evaluate an action via `/actions/submit`."""
        payload: ActionSubmitRequest = {"action": action, "actor": actor}
        if value is not None:
            payload["value"] = value
        if target is not None:
            payload["target"] = target
        if domain is not None:
            payload["domain"] = domain
        if context is not None:
            payload["context"] = context
        elif metadata is not None:
            payload["context"] = metadata
        return await self._transport.request(
            method="POST",
            path="/actions/submit",
            json_body=payload,
            idempotency_key=idempotency_key,
        )

    evaluate = submit

    @overload
    async def submit_v2(self, *, payload: ActionSubmitV2Request, idempotency_key: Optional[str] = None) -> JSONDict:
        ...

    @overload
    async def submit_v2(self, *, payload: ActionSubmitV2Model, idempotency_key: Optional[str] = None) -> JSONDict:
        ...

    async def submit_v2(
        self,
        *,
        payload: ActionSubmitV2Request | ActionSubmitV2Model,
        idempotency_key: Optional[str] = None,
    ) -> JSONDict:
        """Evaluate action via `/actions/submit/v2`."""
        body = to_payload(payload)
        if "context" not in body and "metadata" in body:
            body["context"] = body["metadata"]
        return await self._transport.request(
            method="POST",
            path="/actions/submit/v2",
            json_body=body,
            idempotency_key=idempotency_key,
        )

    @overload
    async def dry_run(self, *, payload: ActionSubmitV2Request, idempotency_key: Optional[str] = None) -> JSONDict:
        ...

    @overload
    async def dry_run(self, *, payload: ActionSubmitV2Model, idempotency_key: Optional[str] = None) -> JSONDict:
        ...

    async def dry_run(
        self,
        *,
        payload: ActionSubmitV2Request | ActionSubmitV2Model,
        idempotency_key: Optional[str] = None,
    ) -> JSONDict:
        """Run a non-persistent evaluation via `/actions/submit/dry-run`."""
        body = to_payload(payload)
        if "context" not in body and "metadata" in body:
            body["context"] = body["metadata"]
        return await self._transport.request(
            method="POST",
            path="/actions/submit/dry-run",
            json_body=body,
            idempotency_key=idempotency_key,
        )

    async def verify_validation(self, validation_id: str) -> JSONDict:
        return await self._transport.request(
            method="GET",
            path=f"/actions/validations/{validation_id}/verify",
        )

    async def observer_stats(self) -> JSONDict:
        return await self._transport.request(method="GET", path="/actions/observer/stats")

    async def dashboard_summary(self) -> JSONDict:
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
    ) -> JSONDict:
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
    ) -> JSONDict:
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

    async def refresh_memory_aggregates(self, *, concurrent: bool = False, window_hours: int = 24) -> JSONDict:
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
    ) -> JSONDict:
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
