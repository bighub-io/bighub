from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..types import JSONDict

_Sync = Any
_Async = Any


class PrecedentsAPI:
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
        intent: Optional[str] = None,
        min_similarity: Optional[float] = None,
        max_results: Optional[int] = None,
        require_outcome: Optional[bool] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {"domain": domain, "action": action, "actor_type": actor_type}
        if tool is not None:
            body["tool"] = tool
        if axes is not None:
            body["axes"] = axes
        if risk_score is not None:
            body["risk_score"] = risk_score
        if intent is not None:
            body["intent"] = intent
        if min_similarity is not None:
            body["min_similarity"] = min_similarity
        if max_results is not None:
            body["max_results"] = max_results
        if require_outcome is not None:
            body["require_outcome"] = require_outcome
        return self._transport.request(
            method="POST", path="/precedents/query", json_body=body
        )

    def signals(
        self,
        *,
        domain: str,
        tool: Optional[str] = None,
        action: str,
        actor_type: str = "AI_AGENT",
        axes: Optional[JSONDict] = None,
        risk_score: Optional[float] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {"domain": domain, "action": action, "actor_type": actor_type}
        if tool is not None:
            body["tool"] = tool
        if axes is not None:
            body["axes"] = axes
        if risk_score is not None:
            body["risk_score"] = risk_score
        return self._transport.request(
            method="POST", path="/precedents/signals", json_body=body
        )

    def stats(self) -> JSONDict:
        return self._transport.request(method="GET", path="/precedents/stats")


class AsyncPrecedentsAPI:
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
        intent: Optional[str] = None,
        min_similarity: Optional[float] = None,
        max_results: Optional[int] = None,
        require_outcome: Optional[bool] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {"domain": domain, "action": action, "actor_type": actor_type}
        if tool is not None:
            body["tool"] = tool
        if axes is not None:
            body["axes"] = axes
        if risk_score is not None:
            body["risk_score"] = risk_score
        if intent is not None:
            body["intent"] = intent
        if min_similarity is not None:
            body["min_similarity"] = min_similarity
        if max_results is not None:
            body["max_results"] = max_results
        if require_outcome is not None:
            body["require_outcome"] = require_outcome
        return await self._transport.request(
            method="POST", path="/precedents/query", json_body=body
        )

    async def signals(
        self,
        *,
        domain: str,
        tool: Optional[str] = None,
        action: str,
        actor_type: str = "AI_AGENT",
        axes: Optional[JSONDict] = None,
        risk_score: Optional[float] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {"domain": domain, "action": action, "actor_type": actor_type}
        if tool is not None:
            body["tool"] = tool
        if axes is not None:
            body["axes"] = axes
        if risk_score is not None:
            body["risk_score"] = risk_score
        return await self._transport.request(
            method="POST", path="/precedents/signals", json_body=body
        )

    async def stats(self) -> JSONDict:
        return await self._transport.request(method="GET", path="/precedents/stats")
