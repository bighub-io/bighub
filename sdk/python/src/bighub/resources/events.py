from __future__ import annotations

from typing import Dict, Optional

from ..protocols import AsyncTransportProtocol, SyncTransportProtocol
from ..types import EventsListResponse, JSONDict


class EventsAPI:
    """Sync API for dashboard event stream endpoints."""

    def __init__(self, transport: SyncTransportProtocol) -> None:
        self._transport = transport

    def list(
        self,
        *,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        rule_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> EventsListResponse:
        params: Dict[str, Any] = {}
        if event_type is not None:
            params["event_type"] = event_type
        if severity is not None:
            params["severity"] = severity
        if rule_id is not None:
            params["rule_id"] = rule_id
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return self._transport.request(method="GET", path="/events", params=params)

    def stats(self) -> JSONDict:
        return self._transport.request(method="GET", path="/events/stats")


class AsyncEventsAPI:
    """Async API for dashboard event stream endpoints."""

    def __init__(self, transport: AsyncTransportProtocol) -> None:
        self._transport = transport

    async def list(
        self,
        *,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        rule_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> EventsListResponse:
        params: Dict[str, Any] = {}
        if event_type is not None:
            params["event_type"] = event_type
        if severity is not None:
            params["severity"] = severity
        if rule_id is not None:
            params["rule_id"] = rule_id
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return await self._transport.request(method="GET", path="/events", params=params)

    async def stats(self) -> JSONDict:
        return await self._transport.request(method="GET", path="/events/stats")
