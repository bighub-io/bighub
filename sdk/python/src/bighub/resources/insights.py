from __future__ import annotations

from typing import Any, Dict, Optional

from ..types import JSONDict

_Sync = Any
_Async = Any


class InsightsAPI:
    def __init__(self, transport: _Sync) -> None:
        self._transport = transport

    def advise(
        self,
        *,
        tool: str,
        action: str,
        domain: str,
        actor_type: str = "AI_AGENT",
        risk_band: Optional[str] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {
            "tool": tool,
            "action": action,
            "domain": domain,
            "actor_type": actor_type,
        }
        if risk_band is not None:
            body["risk_band"] = risk_band
        return self._transport.request(
            method="POST", path="/insights/advise", json_body=body
        )

    def patterns(
        self,
        *,
        pattern_type: Optional[str] = None,
        domain: Optional[str] = None,
        tool: Optional[str] = None,
        min_severity: Optional[str] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {}
        if pattern_type is not None:
            params["pattern_type"] = pattern_type
        if domain is not None:
            params["domain"] = domain
        if tool is not None:
            params["tool"] = tool
        if min_severity is not None:
            params["min_severity"] = min_severity
        return self._transport.request(
            method="GET", path="/insights/patterns", params=params
        )

    def learn(self) -> JSONDict:
        return self._transport.request(method="GET", path="/insights/patterns/learn")

    def profile(
        self,
        *,
        tool: Optional[str] = None,
        action: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {}
        if tool is not None:
            params["tool"] = tool
        if action is not None:
            params["action"] = action
        if domain is not None:
            params["domain"] = domain
        return self._transport.request(
            method="GET", path="/insights/profile", params=params
        )


class AsyncInsightsAPI:
    def __init__(self, transport: _Async) -> None:
        self._transport = transport

    async def advise(
        self,
        *,
        tool: str,
        action: str,
        domain: str,
        actor_type: str = "AI_AGENT",
        risk_band: Optional[str] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {
            "tool": tool,
            "action": action,
            "domain": domain,
            "actor_type": actor_type,
        }
        if risk_band is not None:
            body["risk_band"] = risk_band
        return await self._transport.request(
            method="POST", path="/insights/advise", json_body=body
        )

    async def patterns(
        self,
        *,
        pattern_type: Optional[str] = None,
        domain: Optional[str] = None,
        tool: Optional[str] = None,
        min_severity: Optional[str] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {}
        if pattern_type is not None:
            params["pattern_type"] = pattern_type
        if domain is not None:
            params["domain"] = domain
        if tool is not None:
            params["tool"] = tool
        if min_severity is not None:
            params["min_severity"] = min_severity
        return await self._transport.request(
            method="GET", path="/insights/patterns", params=params
        )

    async def learn(self) -> JSONDict:
        return await self._transport.request(
            method="GET", path="/insights/patterns/learn"
        )

    async def profile(
        self,
        *,
        tool: Optional[str] = None,
        action: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {}
        if tool is not None:
            params["tool"] = tool
        if action is not None:
            params["action"] = action
        if domain is not None:
            params["domain"] = domain
        return await self._transport.request(
            method="GET", path="/insights/profile", params=params
        )
