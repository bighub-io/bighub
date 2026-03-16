from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..types import JSONDict

_Sync = Any
_Async = Any


class RetrievalAPI:
    def __init__(self, transport: _Sync) -> None:
        self._transport = transport

    def query(
        self,
        *,
        domain: str,
        tool: Optional[str] = None,
        action: str,
        actor_type: str = "AI_AGENT",
        axes: Optional[JSONDict] = None,
        risk_score: Optional[float] = None,
        strategy: str = "balanced",
        strategy_name: Optional[str] = None,
    ) -> JSONDict:
        resolved_strategy = strategy_name or strategy
        body: Dict[str, Any] = {
            "domain": domain,
            "action": action,
            "actor_type": actor_type,
            "strategy": resolved_strategy,
            "strategy_name": resolved_strategy,
        }
        if tool is not None:
            body["tool"] = tool
        if axes is not None:
            body["axes"] = axes
        if risk_score is not None:
            body["risk_score"] = risk_score
        return self._transport.request(
            method="POST", path="/retrieval/query", json_body=body
        )

    def query_explained(
        self,
        *,
        domain: str,
        tool: Optional[str] = None,
        action: str,
        actor_type: str = "AI_AGENT",
        axes: Optional[JSONDict] = None,
        risk_score: Optional[float] = None,
        strategy: str = "balanced",
        strategy_name: Optional[str] = None,
    ) -> JSONDict:
        resolved_strategy = strategy_name or strategy
        body: Dict[str, Any] = {
            "domain": domain,
            "action": action,
            "actor_type": actor_type,
            "strategy": resolved_strategy,
            "strategy_name": resolved_strategy,
        }
        if tool is not None:
            body["tool"] = tool
        if axes is not None:
            body["axes"] = axes
        if risk_score is not None:
            body["risk_score"] = risk_score
        return self._transport.request(
            method="POST", path="/retrieval/query/explained", json_body=body
        )

    def strategies(self) -> JSONDict:
        return self._transport.request(method="GET", path="/retrieval/strategies")

    def strategy(self, name: str) -> JSONDict:
        return self._transport.request(
            method="GET", path=f"/retrieval/strategy/{name}"
        )

    def index_case(
        self,
        *,
        case_id: str,
        org_id: str,
        tool: str,
        action: str,
        domain: str,
        actor_type: str = "AI_AGENT",
        risk_score: float = 0.0,
        verdict: str = "ALLOWED",
        axes: Optional[JSONDict] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {
            "case_id": case_id,
            "org_id": org_id,
            "tool": tool,
            "action": action,
            "domain": domain,
            "actor_type": actor_type,
            "risk_score": risk_score,
            "verdict": verdict,
        }
        if axes is not None:
            body["axes"] = axes
        return self._transport.request(
            method="POST", path="/retrieval/index", json_body=body
        )

    def stats(self) -> JSONDict:
        return self._transport.request(method="GET", path="/retrieval/stats")


class AsyncRetrievalAPI:
    def __init__(self, transport: _Async) -> None:
        self._transport = transport

    async def query(
        self,
        *,
        domain: str,
        tool: Optional[str] = None,
        action: str,
        actor_type: str = "AI_AGENT",
        axes: Optional[JSONDict] = None,
        risk_score: Optional[float] = None,
        strategy: str = "balanced",
        strategy_name: Optional[str] = None,
    ) -> JSONDict:
        resolved_strategy = strategy_name or strategy
        body: Dict[str, Any] = {
            "domain": domain,
            "action": action,
            "actor_type": actor_type,
            "strategy": resolved_strategy,
            "strategy_name": resolved_strategy,
        }
        if tool is not None:
            body["tool"] = tool
        if axes is not None:
            body["axes"] = axes
        if risk_score is not None:
            body["risk_score"] = risk_score
        return await self._transport.request(
            method="POST", path="/retrieval/query", json_body=body
        )

    async def query_explained(
        self,
        *,
        domain: str,
        tool: Optional[str] = None,
        action: str,
        actor_type: str = "AI_AGENT",
        axes: Optional[JSONDict] = None,
        risk_score: Optional[float] = None,
        strategy: str = "balanced",
        strategy_name: Optional[str] = None,
    ) -> JSONDict:
        resolved_strategy = strategy_name or strategy
        body: Dict[str, Any] = {
            "domain": domain,
            "action": action,
            "actor_type": actor_type,
            "strategy": resolved_strategy,
            "strategy_name": resolved_strategy,
        }
        if tool is not None:
            body["tool"] = tool
        if axes is not None:
            body["axes"] = axes
        if risk_score is not None:
            body["risk_score"] = risk_score
        return await self._transport.request(
            method="POST", path="/retrieval/query/explained", json_body=body
        )

    async def strategies(self) -> JSONDict:
        return await self._transport.request(
            method="GET", path="/retrieval/strategies"
        )

    async def strategy(self, name: str) -> JSONDict:
        return await self._transport.request(
            method="GET", path=f"/retrieval/strategy/{name}"
        )

    async def index_case(
        self,
        *,
        case_id: str,
        org_id: str,
        tool: str,
        action: str,
        domain: str,
        actor_type: str = "AI_AGENT",
        risk_score: float = 0.0,
        verdict: str = "ALLOWED",
        axes: Optional[JSONDict] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {
            "case_id": case_id,
            "org_id": org_id,
            "tool": tool,
            "action": action,
            "domain": domain,
            "actor_type": actor_type,
            "risk_score": risk_score,
            "verdict": verdict,
        }
        if axes is not None:
            body["axes"] = axes
        return await self._transport.request(
            method="POST", path="/retrieval/index", json_body=body
        )

    async def stats(self) -> JSONDict:
        return await self._transport.request(method="GET", path="/retrieval/stats")
