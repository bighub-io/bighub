from __future__ import annotations

from typing import Any, Dict, Optional

from ..protocols import AsyncTransportProtocol, SyncTransportProtocol


class KillSwitchAPI:
    def __init__(self, transport: SyncTransportProtocol) -> None:
        self._transport = transport

    def status(self) -> Dict[str, Any]:
        return self._transport.request(method="GET", path="/kill-switch/status")

    def activate(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._transport.request(
            method="POST",
            path="/kill-switch/activate",
            json_body=payload or {},
        )

    def deactivate(self, switch_id: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._transport.request(
            method="POST",
            path=f"/kill-switch/deactivate/{switch_id}",
            json_body=payload or {},
        )


class AsyncKillSwitchAPI:
    def __init__(self, transport: AsyncTransportProtocol) -> None:
        self._transport = transport

    async def status(self) -> Dict[str, Any]:
        return await self._transport.request(method="GET", path="/kill-switch/status")

    async def activate(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._transport.request(
            method="POST",
            path="/kill-switch/activate",
            json_body=payload or {},
        )

    async def deactivate(self, switch_id: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._transport.request(
            method="POST",
            path=f"/kill-switch/deactivate/{switch_id}",
            json_body=payload or {},
        )
