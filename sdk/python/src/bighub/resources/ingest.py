from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..types import JSONDict

_Sync = Any
_Async = Any


class IngestAPI:
    def __init__(self, transport: _Sync) -> None:
        self._transport = transport

    def event(
        self,
        *,
        event_type: str,
        timestamp: Optional[str] = None,
        request_id: Optional[str] = None,
        case_id: Optional[str] = None,
        validation_id: Optional[str] = None,
        external_ref: Optional[str] = None,
        action: Optional[JSONDict] = None,
        context: Optional[JSONDict] = None,
        execution: Optional[JSONDict] = None,
        outcome: Optional[JSONDict] = None,
        adapter: Optional[str] = None,
        domain: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {"event_type": event_type}
        if timestamp is not None:
            body["timestamp"] = timestamp
        if request_id is not None:
            body["request_id"] = request_id
        if case_id is not None:
            body["case_id"] = case_id
        if validation_id is not None:
            body["validation_id"] = validation_id
        if external_ref is not None:
            body["external_ref"] = external_ref
        if action is not None:
            body["action"] = action
        if context is not None:
            body["context"] = context
        if execution is not None:
            body["execution"] = execution
        if outcome is not None:
            body["outcome"] = outcome
        if adapter is not None:
            body["adapter"] = adapter
        if domain is not None:
            body["domain"] = domain
        if tags is not None:
            body["tags"] = tags
        return self._transport.request(method="POST", path="/ingest", json_body=body)

    def batch(self, events: List[JSONDict]) -> JSONDict:
        return self._transport.request(
            method="POST", path="/ingest/batch", json_body={"events": events}
        )

    def reconcile(
        self,
        *,
        key_name: Optional[str] = None,
        key_value: Optional[str] = None,
        outcome: Optional[JSONDict] = None,
        request_id: Optional[str] = None,
        case_id: Optional[str] = None,
        external_ref: Optional[str] = None,
        tenant_ref: Optional[str] = None,
        entity_id: Optional[str] = None,
    ) -> JSONDict:
        resolved_key_name = key_name
        resolved_key_value = key_value
        if resolved_key_name is None or resolved_key_value is None:
            for legacy_name, legacy_value in (
                ("request_id", request_id),
                ("case_id", case_id),
                ("external_ref", external_ref),
                ("tenant_ref", tenant_ref),
                ("entity_id", entity_id),
            ):
                if legacy_value is not None:
                    resolved_key_name = legacy_name
                    resolved_key_value = legacy_value
                    break
        if resolved_key_name is None or resolved_key_value is None:
            raise ValueError("reconcile() requires key_name/key_value or a legacy key argument")
        if outcome is None:
            raise ValueError("reconcile() requires outcome payload")
        body: Dict[str, Any] = {
            "key_name": resolved_key_name,
            "key_value": resolved_key_value,
            "outcome": outcome,
        }
        return self._transport.request(
            method="POST", path="/ingest/reconcile", json_body=body
        )

    def lifecycles(
        self,
        *,
        status_filter: Optional[str] = None,
        limit: int = 50,
    ) -> JSONDict:
        params: Dict[str, Any] = {"limit": limit}
        if status_filter is not None:
            params["status_filter"] = status_filter
        return self._transport.request(
            method="GET", path="/ingest/lifecycles", params=params
        )

    def lifecycle(
        self,
        *,
        request_id: Optional[str] = None,
        case_id: Optional[str] = None,
        external_ref: Optional[str] = None,
        tenant_ref: Optional[str] = None,
        entity_id: Optional[str] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {}
        if request_id is not None:
            params["request_id"] = request_id
        if case_id is not None:
            params["case_id"] = case_id
        if external_ref is not None:
            params["external_ref"] = external_ref
        if tenant_ref is not None:
            params["tenant_ref"] = tenant_ref
        if entity_id is not None:
            params["entity_id"] = entity_id
        return self._transport.request(
            method="GET", path="/ingest/lifecycle", params=params
        )

    def pending(self, *, limit: int = 50) -> JSONDict:
        return self._transport.request(
            method="GET", path="/ingest/pending", params={"limit": limit}
        )

    def stale(
        self,
        *,
        stale_after_days: int = 7,
        limit: int = 50,
    ) -> JSONDict:
        return self._transport.request(
            method="GET",
            path="/ingest/stale",
            params={"stale_after_days": stale_after_days, "limit": limit},
        )

    def stats(self) -> JSONDict:
        return self._transport.request(method="GET", path="/ingest/stats")


class AsyncIngestAPI:
    def __init__(self, transport: _Async) -> None:
        self._transport = transport

    async def event(
        self,
        *,
        event_type: str,
        timestamp: Optional[str] = None,
        request_id: Optional[str] = None,
        case_id: Optional[str] = None,
        validation_id: Optional[str] = None,
        external_ref: Optional[str] = None,
        action: Optional[JSONDict] = None,
        context: Optional[JSONDict] = None,
        execution: Optional[JSONDict] = None,
        outcome: Optional[JSONDict] = None,
        adapter: Optional[str] = None,
        domain: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {"event_type": event_type}
        if timestamp is not None:
            body["timestamp"] = timestamp
        if request_id is not None:
            body["request_id"] = request_id
        if case_id is not None:
            body["case_id"] = case_id
        if validation_id is not None:
            body["validation_id"] = validation_id
        if external_ref is not None:
            body["external_ref"] = external_ref
        if action is not None:
            body["action"] = action
        if context is not None:
            body["context"] = context
        if execution is not None:
            body["execution"] = execution
        if outcome is not None:
            body["outcome"] = outcome
        if adapter is not None:
            body["adapter"] = adapter
        if domain is not None:
            body["domain"] = domain
        if tags is not None:
            body["tags"] = tags
        return await self._transport.request(
            method="POST", path="/ingest", json_body=body
        )

    async def batch(self, events: List[JSONDict]) -> JSONDict:
        return await self._transport.request(
            method="POST", path="/ingest/batch", json_body={"events": events}
        )

    async def reconcile(
        self,
        *,
        key_name: Optional[str] = None,
        key_value: Optional[str] = None,
        outcome: Optional[JSONDict] = None,
        request_id: Optional[str] = None,
        case_id: Optional[str] = None,
        external_ref: Optional[str] = None,
        tenant_ref: Optional[str] = None,
        entity_id: Optional[str] = None,
    ) -> JSONDict:
        resolved_key_name = key_name
        resolved_key_value = key_value
        if resolved_key_name is None or resolved_key_value is None:
            for legacy_name, legacy_value in (
                ("request_id", request_id),
                ("case_id", case_id),
                ("external_ref", external_ref),
                ("tenant_ref", tenant_ref),
                ("entity_id", entity_id),
            ):
                if legacy_value is not None:
                    resolved_key_name = legacy_name
                    resolved_key_value = legacy_value
                    break
        if resolved_key_name is None or resolved_key_value is None:
            raise ValueError("reconcile() requires key_name/key_value or a legacy key argument")
        if outcome is None:
            raise ValueError("reconcile() requires outcome payload")
        body: Dict[str, Any] = {
            "key_name": resolved_key_name,
            "key_value": resolved_key_value,
            "outcome": outcome,
        }
        return await self._transport.request(
            method="POST", path="/ingest/reconcile", json_body=body
        )

    async def lifecycles(
        self,
        *,
        status_filter: Optional[str] = None,
        limit: int = 50,
    ) -> JSONDict:
        params: Dict[str, Any] = {"limit": limit}
        if status_filter is not None:
            params["status_filter"] = status_filter
        return await self._transport.request(
            method="GET", path="/ingest/lifecycles", params=params
        )

    async def lifecycle(
        self,
        *,
        request_id: Optional[str] = None,
        case_id: Optional[str] = None,
        external_ref: Optional[str] = None,
        tenant_ref: Optional[str] = None,
        entity_id: Optional[str] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {}
        if request_id is not None:
            params["request_id"] = request_id
        if case_id is not None:
            params["case_id"] = case_id
        if external_ref is not None:
            params["external_ref"] = external_ref
        if tenant_ref is not None:
            params["tenant_ref"] = tenant_ref
        if entity_id is not None:
            params["entity_id"] = entity_id
        return await self._transport.request(
            method="GET", path="/ingest/lifecycle", params=params
        )

    async def pending(self, *, limit: int = 50) -> JSONDict:
        return await self._transport.request(
            method="GET", path="/ingest/pending", params={"limit": limit}
        )

    async def stale(
        self,
        *,
        stale_after_days: int = 7,
        limit: int = 50,
    ) -> JSONDict:
        return await self._transport.request(
            method="GET",
            path="/ingest/stale",
            params={"stale_after_days": stale_after_days, "limit": limit},
        )

    async def stats(self) -> JSONDict:
        return await self._transport.request(method="GET", path="/ingest/stats")
