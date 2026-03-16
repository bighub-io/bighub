from __future__ import annotations

from typing import Any, Dict

from ..types import JSONDict

_Sync = Any
_Async = Any


class LearningAPI:
    def __init__(self, transport: _Sync) -> None:
        self._transport = transport

    def strategy(self) -> JSONDict:
        return self._transport.request(method="GET", path="/ops/learning/strategy")

    def runs(self, *, limit: int = 50) -> JSONDict:
        return self._transport.request(
            method="GET", path="/ops/learning/runs", params={"limit": limit}
        )

    def recompute(
        self,
        *,
        domain: str = "",
        action_family: str = "",
        force: bool = False,
        limit: int = 5000,
        async_mode: bool = True,
    ) -> JSONDict:
        body: Dict[str, Any] = {
            "domain": domain,
            "action_family": action_family,
            "force": force,
            "limit": limit,
            "async_mode": async_mode,
        }
        return self._transport.request(
            method="POST", path="/ops/learning/recompute", json_body=body
        )

    def backfill(
        self,
        *,
        domain: str = "",
        action_family: str = "",
        force: bool = False,
        limit: int = 5000,
        async_mode: bool = True,
    ) -> JSONDict:
        body: Dict[str, Any] = {
            "domain": domain,
            "action_family": action_family,
            "force": force,
            "limit": limit,
            "async_mode": async_mode,
        }
        return self._transport.request(
            method="POST", path="/ops/learning/backfill", json_body=body
        )


class AsyncLearningAPI:
    def __init__(self, transport: _Async) -> None:
        self._transport = transport

    async def strategy(self) -> JSONDict:
        return await self._transport.request(
            method="GET", path="/ops/learning/strategy"
        )

    async def runs(self, *, limit: int = 50) -> JSONDict:
        return await self._transport.request(
            method="GET", path="/ops/learning/runs", params={"limit": limit}
        )

    async def recompute(
        self,
        *,
        domain: str = "",
        action_family: str = "",
        force: bool = False,
        limit: int = 5000,
        async_mode: bool = True,
    ) -> JSONDict:
        body: Dict[str, Any] = {
            "domain": domain,
            "action_family": action_family,
            "force": force,
            "limit": limit,
            "async_mode": async_mode,
        }
        return await self._transport.request(
            method="POST", path="/ops/learning/recompute", json_body=body
        )

    async def backfill(
        self,
        *,
        domain: str = "",
        action_family: str = "",
        force: bool = False,
        limit: int = 5000,
        async_mode: bool = True,
    ) -> JSONDict:
        body: Dict[str, Any] = {
            "domain": domain,
            "action_family": action_family,
            "force": force,
            "limit": limit,
            "async_mode": async_mode,
        }
        return await self._transport.request(
            method="POST", path="/ops/learning/backfill", json_body=body
        )
