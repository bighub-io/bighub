from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..protocols import AsyncTransportProtocol, SyncTransportProtocol
from ..types import JSONDict


class CasesAPI:
    """Decision case lifecycle: create, get, list, report outcome, precedents, calibration."""

    def __init__(self, transport: SyncTransportProtocol) -> None:
        self._transport = transport

    def create(
        self,
        *,
        domain: str,
        action: JSONDict,
        verdict: JSONDict,
        context: Optional[JSONDict] = None,
        simulation: Optional[JSONDict] = None,
        goal_summary: str = "",
        trigger_source: str = "",
        actor_type: str = "AI_AGENT",
        actor_id: str = "",
        agent_model: str = "",
        refs: Optional[JSONDict] = None,
        tags: Optional[List[str]] = None,
    ) -> JSONDict:
        """Create a decision case."""
        body: Dict[str, Any] = {"domain": domain, "action": action}
        if context:
            body["context"] = context
        if simulation:
            body["simulation"] = simulation
        body["verdict"] = verdict
        if goal_summary:
            body["goal_summary"] = goal_summary
        if trigger_source:
            body["trigger_source"] = trigger_source
        if actor_type != "AI_AGENT":
            body["actor_type"] = actor_type
        if actor_id:
            body["actor_id"] = actor_id
        if agent_model:
            body["agent_model"] = agent_model
        if refs:
            body["refs"] = refs
        if tags:
            body["tags"] = tags
        return self._transport.request(method="POST", path="/cases", json_body=body)

    def get(self, case_id: str) -> JSONDict:
        """Get a decision case by ID."""
        return self._transport.request(method="GET", path=f"/cases/{case_id}")

    def list(
        self,
        *,
        domain: Optional[str] = None,
        tool: Optional[str] = None,
        action: Optional[str] = None,
        verdict: Optional[str] = None,
        outcome_status: Optional[str] = None,
        has_outcome: Optional[bool] = None,
        min_risk_score: Optional[float] = None,
        max_risk_score: Optional[float] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> JSONDict:
        """List decision cases with filters."""
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if domain:
            params["domain"] = domain
        if tool:
            params["tool"] = tool
        if action:
            params["action"] = action
        if verdict:
            params["verdict"] = verdict
        if outcome_status:
            params["outcome_status"] = outcome_status
        if has_outcome is not None:
            params["has_outcome"] = has_outcome
        if min_risk_score is not None:
            params["min_risk_score"] = min_risk_score
        if max_risk_score is not None:
            params["max_risk_score"] = max_risk_score
        return self._transport.request(method="GET", path="/cases", params=params)

    def report_outcome(
        self,
        case_id: str,
        *,
        status: str,
        description: str = "",
        details: Optional[JSONDict] = None,
        actual_impact: Optional[JSONDict] = None,
        correction_needed: bool = False,
        rollback_performed: bool = False,
        revenue_impact: Optional[float] = None,
    ) -> JSONDict:
        """Report a real-world outcome for a decision case."""
        body: Dict[str, Any] = {"status": status}
        if description:
            body["description"] = description
        if details:
            body["details"] = details
        if actual_impact:
            body["actual_impact"] = actual_impact
        if correction_needed:
            body["correction_needed"] = True
        if rollback_performed:
            body["rollback_performed"] = True
        if revenue_impact is not None:
            body["revenue_impact"] = revenue_impact
        return self._transport.request(
            method="POST", path=f"/cases/{case_id}/outcome", json_body=body
        )

    def precedents(
        self,
        *,
        domain: str = "",
        action: str,
        tool: Optional[str] = None,
        actor_type: Optional[str] = None,
        action_type: Optional[str] = None,
        arguments: Optional[JSONDict] = None,
        value: Optional[float] = None,
        target: Optional[str] = None,
        axes: Optional[Dict[str, float]] = None,
        axes_risk_score: Optional[float] = None,
        intent: Optional[str] = None,
        min_similarity: float = 0.5,
        limit: int = 20,
    ) -> JSONDict:
        """Get precedent intelligence for a proposed action.

        Sends nested ActionInput / ContextInput objects matching the backend
        PrecedentRequest schema.
        """
        action_input: Dict[str, Any] = {"action": action}
        if tool:
            action_input["tool"] = tool
        if actor_type:
            action_input["action_type"] = actor_type
        if action_type:
            action_input["action_type"] = action_type
        if arguments:
            action_input["arguments"] = arguments
        if value is not None:
            action_input["value"] = value
        if target:
            action_input["target"] = target

        context_input: Dict[str, Any] = {}
        if axes:
            context_input["axes"] = axes
        if axes_risk_score is not None:
            context_input["axes_risk_score"] = axes_risk_score
        if intent:
            context_input["intent"] = intent

        body: Dict[str, Any] = {
            "domain": domain,
            "action": action_input,
            "min_similarity": min_similarity,
            "limit": limit,
        }
        if context_input:
            body["context"] = context_input
        return self._transport.request(
            method="POST", path="/cases/precedents", json_body=body
        )

    def calibration(self, *, domain: Optional[str] = None) -> JSONDict:
        """Get calibration metrics (prediction vs reality)."""
        params: Dict[str, Any] = {}
        if domain:
            params["domain"] = domain
        return self._transport.request(
            method="GET", path="/cases/calibration", params=params
        )


class AsyncCasesAPI:
    """Async decision case lifecycle."""

    def __init__(self, transport: AsyncTransportProtocol) -> None:
        self._transport = transport

    async def create(
        self,
        *,
        domain: str,
        action: JSONDict,
        verdict: JSONDict,
        context: Optional[JSONDict] = None,
        simulation: Optional[JSONDict] = None,
        goal_summary: str = "",
        trigger_source: str = "",
        actor_type: str = "AI_AGENT",
        actor_id: str = "",
        agent_model: str = "",
        refs: Optional[JSONDict] = None,
        tags: Optional[List[str]] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {"domain": domain, "action": action}
        if context:
            body["context"] = context
        if simulation:
            body["simulation"] = simulation
        body["verdict"] = verdict
        if goal_summary:
            body["goal_summary"] = goal_summary
        if trigger_source:
            body["trigger_source"] = trigger_source
        if actor_type != "AI_AGENT":
            body["actor_type"] = actor_type
        if actor_id:
            body["actor_id"] = actor_id
        if agent_model:
            body["agent_model"] = agent_model
        if refs:
            body["refs"] = refs
        if tags:
            body["tags"] = tags
        return await self._transport.request(
            method="POST", path="/cases", json_body=body
        )

    async def get(self, case_id: str) -> JSONDict:
        return await self._transport.request(
            method="GET", path=f"/cases/{case_id}"
        )

    async def list(
        self,
        *,
        domain: Optional[str] = None,
        tool: Optional[str] = None,
        action: Optional[str] = None,
        verdict: Optional[str] = None,
        outcome_status: Optional[str] = None,
        has_outcome: Optional[bool] = None,
        min_risk_score: Optional[float] = None,
        max_risk_score: Optional[float] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> JSONDict:
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if domain:
            params["domain"] = domain
        if tool:
            params["tool"] = tool
        if action:
            params["action"] = action
        if verdict:
            params["verdict"] = verdict
        if outcome_status:
            params["outcome_status"] = outcome_status
        if has_outcome is not None:
            params["has_outcome"] = has_outcome
        if min_risk_score is not None:
            params["min_risk_score"] = min_risk_score
        if max_risk_score is not None:
            params["max_risk_score"] = max_risk_score
        return await self._transport.request(
            method="GET", path="/cases", params=params
        )

    async def report_outcome(
        self,
        case_id: str,
        *,
        status: str,
        description: str = "",
        details: Optional[JSONDict] = None,
        actual_impact: Optional[JSONDict] = None,
        correction_needed: bool = False,
        rollback_performed: bool = False,
        revenue_impact: Optional[float] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {"status": status}
        if description:
            body["description"] = description
        if details:
            body["details"] = details
        if actual_impact:
            body["actual_impact"] = actual_impact
        if correction_needed:
            body["correction_needed"] = True
        if rollback_performed:
            body["rollback_performed"] = True
        if revenue_impact is not None:
            body["revenue_impact"] = revenue_impact
        return await self._transport.request(
            method="POST", path=f"/cases/{case_id}/outcome", json_body=body
        )

    async def precedents(
        self,
        *,
        domain: str = "",
        action: str,
        tool: Optional[str] = None,
        actor_type: Optional[str] = None,
        action_type: Optional[str] = None,
        arguments: Optional[JSONDict] = None,
        value: Optional[float] = None,
        target: Optional[str] = None,
        axes: Optional[Dict[str, float]] = None,
        axes_risk_score: Optional[float] = None,
        intent: Optional[str] = None,
        min_similarity: float = 0.5,
        limit: int = 20,
    ) -> JSONDict:
        action_input: Dict[str, Any] = {"action": action}
        if tool:
            action_input["tool"] = tool
        if actor_type:
            action_input["action_type"] = actor_type
        if action_type:
            action_input["action_type"] = action_type
        if arguments:
            action_input["arguments"] = arguments
        if value is not None:
            action_input["value"] = value
        if target:
            action_input["target"] = target

        context_input: Dict[str, Any] = {}
        if axes:
            context_input["axes"] = axes
        if axes_risk_score is not None:
            context_input["axes_risk_score"] = axes_risk_score
        if intent:
            context_input["intent"] = intent

        body: Dict[str, Any] = {
            "domain": domain,
            "action": action_input,
            "min_similarity": min_similarity,
            "limit": limit,
        }
        if context_input:
            body["context"] = context_input
        return await self._transport.request(
            method="POST", path="/cases/precedents", json_body=body
        )

    async def calibration(self, *, domain: Optional[str] = None) -> JSONDict:
        params: Dict[str, Any] = {}
        if domain:
            params["domain"] = domain
        return await self._transport.request(
            method="GET", path="/cases/calibration", params=params
        )
