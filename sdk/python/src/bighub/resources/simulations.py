from __future__ import annotations

from typing import Any, Dict, Optional

from ..types import JSONDict

_Sync = Any
_Async = Any


class SimulationsAPI:
    def __init__(self, transport: _Sync) -> None:
        self._transport = transport

    def list(
        self,
        *,
        domain: Optional[str] = None,
        tool: Optional[str] = None,
        with_outcome: Optional[bool] = None,
        limit: int = 50,
    ) -> JSONDict:
        params: Dict[str, Any] = {"limit": limit}
        if domain is not None:
            params["domain"] = domain
        if tool is not None:
            params["tool"] = tool
        if with_outcome is not None:
            params["with_outcome"] = with_outcome
        return self._transport.request(
            method="GET", path="/simulations", params=params
        )

    def get(self, snapshot_id: str) -> JSONDict:
        return self._transport.request(
            method="GET", path=f"/simulations/{snapshot_id}"
        )

    def by_request(self, request_id: str) -> JSONDict:
        return self._transport.request(
            method="GET", path=f"/simulations/by-request/{request_id}"
        )

    def compare(self, request_id: str) -> JSONDict:
        return self._transport.request(
            method="GET", path=f"/simulations/by-request/{request_id}/compare"
        )

    def accuracy(
        self,
        *,
        domain: Optional[str] = None,
        tool: Optional[str] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {}
        if domain is not None:
            params["domain"] = domain
        if tool is not None:
            params["tool"] = tool
        return self._transport.request(
            method="GET", path="/simulations/accuracy", params=params
        )

    def stats(self) -> JSONDict:
        return self._transport.request(method="GET", path="/simulations/stats")


class AsyncSimulationsAPI:
    def __init__(self, transport: _Async) -> None:
        self._transport = transport

    async def list(
        self,
        *,
        domain: Optional[str] = None,
        tool: Optional[str] = None,
        with_outcome: Optional[bool] = None,
        limit: int = 50,
    ) -> JSONDict:
        params: Dict[str, Any] = {"limit": limit}
        if domain is not None:
            params["domain"] = domain
        if tool is not None:
            params["tool"] = tool
        if with_outcome is not None:
            params["with_outcome"] = with_outcome
        return await self._transport.request(
            method="GET", path="/simulations", params=params
        )

    async def get(self, snapshot_id: str) -> JSONDict:
        return await self._transport.request(
            method="GET", path=f"/simulations/{snapshot_id}"
        )

    async def by_request(self, request_id: str) -> JSONDict:
        return await self._transport.request(
            method="GET", path=f"/simulations/by-request/{request_id}"
        )

    async def compare(self, request_id: str) -> JSONDict:
        return await self._transport.request(
            method="GET", path=f"/simulations/by-request/{request_id}/compare"
        )

    async def accuracy(
        self,
        *,
        domain: Optional[str] = None,
        tool: Optional[str] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {}
        if domain is not None:
            params["domain"] = domain
        if tool is not None:
            params["tool"] = tool
        return await self._transport.request(
            method="GET", path="/simulations/accuracy", params=params
        )

    async def stats(self) -> JSONDict:
        return await self._transport.request(
            method="GET", path="/simulations/stats"
        )
