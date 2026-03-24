from __future__ import annotations

from typing import Any, Dict, List, Optional, overload

from ..models import ApprovalResolveModel
from ..protocols import AsyncTransportProtocol, SyncTransportProtocol
from ..types import ApprovalItem, JSONDict


class ApprovalsAPI:
    """Sync API for approval queue endpoints."""

    def __init__(self, transport: SyncTransportProtocol) -> None:
        self._transport = transport

    def list(self, *, status_filter: str = "pending", limit: Optional[int] = None) -> List[ApprovalItem]:
        params: Dict[str, Any] = {"status": status_filter}
        if limit is not None:
            params["limit"] = limit
        return self._transport.request(method="GET", path="/approvals", params=params)

    @overload
    def resolve(self, request_id: str, *, resolution: str, comment: Optional[str] = None) -> ApprovalItem:
        ...

    @overload
    def resolve(self, request_id: str, *, payload: ApprovalResolveModel) -> ApprovalItem:
        ...

    def resolve(
        self,
        request_id: str,
        *,
        resolution: Optional[str] = None,
        comment: Optional[str] = None,
        payload: Optional[ApprovalResolveModel] = None,
    ) -> ApprovalItem:
        if payload is not None:
            payload_data: Dict[str, Any] = payload.to_payload()
        else:
            if resolution is None:
                raise ValueError("resolution is required when payload is not provided")
            payload_data = {"resolution": resolution}
            if comment is not None:
                payload_data["comment"] = comment
        return self._transport.request(
            method="POST",
            path=f"/approvals/{request_id}/resolve",
            json_body=payload_data,
        )


class AsyncApprovalsAPI:
    """Async API for approval queue endpoints."""

    def __init__(self, transport: AsyncTransportProtocol) -> None:
        self._transport = transport

    async def list(self, *, status_filter: str = "pending", limit: Optional[int] = None) -> List[ApprovalItem]:
        params: Dict[str, Any] = {"status": status_filter}
        if limit is not None:
            params["limit"] = limit
        return await self._transport.request(method="GET", path="/approvals", params=params)

    @overload
    async def resolve(self, request_id: str, *, resolution: str, comment: Optional[str] = None) -> ApprovalItem:
        ...

    @overload
    async def resolve(self, request_id: str, *, payload: ApprovalResolveModel) -> ApprovalItem:
        ...

    async def resolve(
        self,
        request_id: str,
        *,
        resolution: Optional[str] = None,
        comment: Optional[str] = None,
        payload: Optional[ApprovalResolveModel] = None,
    ) -> ApprovalItem:
        if payload is not None:
            payload_data: Dict[str, Any] = payload.to_payload()
        else:
            if resolution is None:
                raise ValueError("resolution is required when payload is not provided")
            payload_data = {"resolution": resolution}
            if comment is not None:
                payload_data["comment"] = comment
        return await self._transport.request(
            method="POST",
            path=f"/approvals/{request_id}/resolve",
            json_body=payload_data,
        )
