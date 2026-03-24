from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..types import JSONDict

_Sync = Any
_Async = Any


class CalibrationAPI:
    def __init__(self, transport: _Sync) -> None:
        self._transport = transport

    def report(
        self,
        *,
        domain: Optional[str] = None,
        tool: Optional[str] = None,
        risk_band: Optional[str] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {}
        if domain is not None:
            params["domain"] = domain
        if tool is not None:
            params["tool"] = tool
        if risk_band is not None:
            params["risk_band"] = risk_band
        return self._transport.request(
            method="GET", path="/calibration/report", params=params
        )

    def reliability(
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
            method="GET", path="/calibration/reliability", params=params
        )

    def drift(
        self,
        *,
        window_days: Optional[int] = None,
        domain: Optional[str] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {}
        if window_days is not None:
            params["window_days"] = window_days
        if domain is not None:
            params["domain"] = domain
        return self._transport.request(
            method="GET", path="/calibration/drift", params=params
        )

    def breakdown(self, *, by: str = "domain") -> JSONDict:
        return self._transport.request(
            method="GET", path="/calibration/breakdown", params={"by": by}
        )

    def feedback(self, *, domain: Optional[str] = None) -> JSONDict:
        params: Dict[str, Any] = {}
        if domain is not None:
            params["domain"] = domain
        return self._transport.request(
            method="GET", path="/calibration/feedback", params=params
        )

    def observe(
        self,
        *,
        case_id: str,
        predicted_risk: float,
        outcome_status: str,
        domain: Optional[str] = None,
        tool: Optional[str] = None,
        action: Optional[str] = None,
        actor_type: Optional[str] = None,
        verdict: Optional[str] = None,
        simulation_failure_rate: Optional[float] = None,
        simulation_fragility: Optional[float] = None,
        simulation_confidence: Optional[float] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {
            "case_id": case_id,
            "predicted_risk": predicted_risk,
            "outcome_status": outcome_status,
        }
        if domain is not None:
            body["domain"] = domain
        if tool is not None:
            body["tool"] = tool
        if action is not None:
            body["action"] = action
        if actor_type is not None:
            body["actor_type"] = actor_type
        if verdict is not None:
            body["verdict"] = verdict
        if simulation_failure_rate is not None:
            body["simulation_failure_rate"] = simulation_failure_rate
        if simulation_fragility is not None:
            body["simulation_fragility"] = simulation_fragility
        if simulation_confidence is not None:
            body["simulation_confidence"] = simulation_confidence
        return self._transport.request(
            method="POST", path="/calibration/observe", json_body=body
        )

    def quality_history(
        self,
        *,
        days: int = 30,
        domain: Optional[str] = None,
    ) -> List[JSONDict]:
        """Daily quality score over time (quality_score, positive_rate per day)."""
        params: Dict[str, Any] = {"days": days}
        if domain is not None:
            params["domain"] = domain
        return self._transport.request(
            method="GET", path="/calibration/quality-history", params=params
        )


class AsyncCalibrationAPI:
    def __init__(self, transport: _Async) -> None:
        self._transport = transport

    async def report(
        self,
        *,
        domain: Optional[str] = None,
        tool: Optional[str] = None,
        risk_band: Optional[str] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {}
        if domain is not None:
            params["domain"] = domain
        if tool is not None:
            params["tool"] = tool
        if risk_band is not None:
            params["risk_band"] = risk_band
        return await self._transport.request(
            method="GET", path="/calibration/report", params=params
        )

    async def reliability(
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
            method="GET", path="/calibration/reliability", params=params
        )

    async def drift(
        self,
        *,
        window_days: Optional[int] = None,
        domain: Optional[str] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {}
        if window_days is not None:
            params["window_days"] = window_days
        if domain is not None:
            params["domain"] = domain
        return await self._transport.request(
            method="GET", path="/calibration/drift", params=params
        )

    async def breakdown(self, *, by: str = "domain") -> JSONDict:
        return await self._transport.request(
            method="GET", path="/calibration/breakdown", params={"by": by}
        )

    async def feedback(self, *, domain: Optional[str] = None) -> JSONDict:
        params: Dict[str, Any] = {}
        if domain is not None:
            params["domain"] = domain
        return await self._transport.request(
            method="GET", path="/calibration/feedback", params=params
        )

    async def observe(
        self,
        *,
        case_id: str,
        predicted_risk: float,
        outcome_status: str,
        domain: Optional[str] = None,
        tool: Optional[str] = None,
        action: Optional[str] = None,
        actor_type: Optional[str] = None,
        verdict: Optional[str] = None,
        simulation_failure_rate: Optional[float] = None,
        simulation_fragility: Optional[float] = None,
        simulation_confidence: Optional[float] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {
            "case_id": case_id,
            "predicted_risk": predicted_risk,
            "outcome_status": outcome_status,
        }
        if domain is not None:
            body["domain"] = domain
        if tool is not None:
            body["tool"] = tool
        if action is not None:
            body["action"] = action
        if actor_type is not None:
            body["actor_type"] = actor_type
        if verdict is not None:
            body["verdict"] = verdict
        if simulation_failure_rate is not None:
            body["simulation_failure_rate"] = simulation_failure_rate
        if simulation_fragility is not None:
            body["simulation_fragility"] = simulation_fragility
        if simulation_confidence is not None:
            body["simulation_confidence"] = simulation_confidence
        return await self._transport.request(
            method="POST", path="/calibration/observe", json_body=body
        )

    async def quality_history(
        self,
        *,
        days: int = 30,
        domain: Optional[str] = None,
    ) -> List[JSONDict]:
        """Daily quality score over time (quality_score, positive_rate per day)."""
        params: Dict[str, Any] = {"days": days}
        if domain is not None:
            params["domain"] = domain
        return await self._transport.request(
            method="GET", path="/calibration/quality-history", params=params
        )
