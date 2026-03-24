from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..protocols import AsyncTransportProtocol, SyncTransportProtocol
from ..types import JSONDict


class OutcomesAPI:
    """Outcome reporting and analytics: report what actually happened after execution."""

    def __init__(self, transport: SyncTransportProtocol) -> None:
        self._transport = transport

    def report(
        self,
        *,
        status: str,
        request_id: Optional[str] = None,
        case_id: Optional[str] = None,
        validation_id: Optional[str] = None,
        description: str = "",
        details: Optional[JSONDict] = None,
        actual_impact: Optional[JSONDict] = None,
        correction_needed: bool = False,
        correction_description: str = "",
        correction_cost: Optional[float] = None,
        time_to_detect_s: Optional[float] = None,
        time_to_resolve_s: Optional[float] = None,
        rollback_performed: bool = False,
        revenue_impact: Optional[float] = None,
        customer_impact_count: int = 0,
        support_tickets_created: int = 0,
        observed_at: Optional[str] = None,
        reported_by: str = "",
        tags: Optional[List[str]] = None,
    ) -> JSONDict:
        """Report a real-world outcome linked to a decision."""
        body: Dict[str, Any] = {"status": status}
        if request_id:
            body["request_id"] = request_id
        if case_id:
            body["case_id"] = case_id
        if validation_id:
            body["validation_id"] = validation_id
        if description:
            body["description"] = description
        if details:
            body["details"] = details
        if actual_impact:
            body["actual_impact"] = actual_impact
        if correction_needed:
            body["correction_needed"] = True
            if correction_description:
                body["correction_description"] = correction_description
            if correction_cost is not None:
                body["correction_cost"] = correction_cost
            if time_to_detect_s is not None:
                body["time_to_detect_s"] = time_to_detect_s
            if time_to_resolve_s is not None:
                body["time_to_resolve_s"] = time_to_resolve_s
        if rollback_performed:
            body["rollback_performed"] = True
        if revenue_impact is not None:
            body["revenue_impact"] = revenue_impact
        if customer_impact_count:
            body["customer_impact_count"] = customer_impact_count
        if support_tickets_created:
            body["support_tickets_created"] = support_tickets_created
        if observed_at:
            body["observed_at"] = observed_at
        if reported_by:
            body["reported_by"] = reported_by
        if tags:
            body["tags"] = tags
        return self._transport.request(
            method="POST", path="/outcomes/report", json_body=body
        )

    def report_batch(self, outcomes: List[JSONDict]) -> JSONDict:
        """Batch report outcomes (max 100)."""
        return self._transport.request(
            method="POST",
            path="/outcomes/report/batch",
            json_body={"outcomes": outcomes},
        )

    def get(self, request_id: str) -> JSONDict:
        """Get outcome by request_id."""
        return self._transport.request(
            method="GET", path=f"/outcomes/{request_id}"
        )

    def get_by_validation(self, validation_id: str) -> JSONDict:
        """Get outcome by validation_id."""
        return self._transport.request(
            method="GET", path=f"/outcomes/by-validation/{validation_id}"
        )

    def get_by_case(self, case_id: str) -> JSONDict:
        """Get outcome by case_id."""
        return self._transport.request(
            method="GET", path=f"/outcomes/by-case/{case_id}"
        )

    def timeline(self, request_id: str) -> JSONDict:
        """Get full outcome timeline for a request."""
        return self._transport.request(
            method="GET", path=f"/outcomes/{request_id}/timeline"
        )

    def pending(
        self,
        *,
        min_age_hours: Optional[int] = None,
        limit: int = 50,
    ) -> JSONDict:
        """List decisions still awaiting outcome reports."""
        params: Dict[str, Any] = {"limit": limit}
        if min_age_hours is not None:
            params["min_age_hours"] = min_age_hours
        return self._transport.request(
            method="GET", path="/outcomes/pending/list", params=params
        )

    def analytics(
        self,
        *,
        domain: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
    ) -> JSONDict:
        """Outcome analytics summary."""
        params: Dict[str, Any] = {}
        if domain:
            params["domain"] = domain
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        return self._transport.request(
            method="GET", path="/outcomes/analytics/summary", params=params
        )

    def taxonomy(self) -> JSONDict:
        """Supported outcome status taxonomy."""
        return self._transport.request(method="GET", path="/outcomes/taxonomy")

    def recommendation_quality(
        self,
        *,
        domain: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
    ) -> JSONDict:
        """Recommendation quality analytics: follow rate, quadrants, by_domain, examples."""
        params: Dict[str, Any] = {}
        if domain:
            params["domain"] = domain
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        return self._transport.request(
            method="GET", path="/outcomes/analytics/recommendation-quality", params=params
        )


class AsyncOutcomesAPI:
    """Async outcome reporting and analytics."""

    def __init__(self, transport: AsyncTransportProtocol) -> None:
        self._transport = transport

    async def report(
        self,
        *,
        status: str,
        request_id: Optional[str] = None,
        case_id: Optional[str] = None,
        validation_id: Optional[str] = None,
        description: str = "",
        details: Optional[JSONDict] = None,
        actual_impact: Optional[JSONDict] = None,
        correction_needed: bool = False,
        correction_description: str = "",
        correction_cost: Optional[float] = None,
        time_to_detect_s: Optional[float] = None,
        time_to_resolve_s: Optional[float] = None,
        rollback_performed: bool = False,
        revenue_impact: Optional[float] = None,
        customer_impact_count: int = 0,
        support_tickets_created: int = 0,
        observed_at: Optional[str] = None,
        reported_by: str = "",
        tags: Optional[List[str]] = None,
    ) -> JSONDict:
        body: Dict[str, Any] = {"status": status}
        if request_id:
            body["request_id"] = request_id
        if case_id:
            body["case_id"] = case_id
        if validation_id:
            body["validation_id"] = validation_id
        if description:
            body["description"] = description
        if details:
            body["details"] = details
        if actual_impact:
            body["actual_impact"] = actual_impact
        if correction_needed:
            body["correction_needed"] = True
            if correction_description:
                body["correction_description"] = correction_description
            if correction_cost is not None:
                body["correction_cost"] = correction_cost
            if time_to_detect_s is not None:
                body["time_to_detect_s"] = time_to_detect_s
            if time_to_resolve_s is not None:
                body["time_to_resolve_s"] = time_to_resolve_s
        if rollback_performed:
            body["rollback_performed"] = True
        if revenue_impact is not None:
            body["revenue_impact"] = revenue_impact
        if customer_impact_count:
            body["customer_impact_count"] = customer_impact_count
        if support_tickets_created:
            body["support_tickets_created"] = support_tickets_created
        if observed_at:
            body["observed_at"] = observed_at
        if reported_by:
            body["reported_by"] = reported_by
        if tags:
            body["tags"] = tags
        return await self._transport.request(
            method="POST", path="/outcomes/report", json_body=body
        )

    async def report_batch(self, outcomes: List[JSONDict]) -> JSONDict:
        return await self._transport.request(
            method="POST",
            path="/outcomes/report/batch",
            json_body={"outcomes": outcomes},
        )

    async def get(self, request_id: str) -> JSONDict:
        return await self._transport.request(
            method="GET", path=f"/outcomes/{request_id}"
        )

    async def get_by_validation(self, validation_id: str) -> JSONDict:
        return await self._transport.request(
            method="GET", path=f"/outcomes/by-validation/{validation_id}"
        )

    async def get_by_case(self, case_id: str) -> JSONDict:
        return await self._transport.request(
            method="GET", path=f"/outcomes/by-case/{case_id}"
        )

    async def timeline(self, request_id: str) -> JSONDict:
        return await self._transport.request(
            method="GET", path=f"/outcomes/{request_id}/timeline"
        )

    async def pending(
        self,
        *,
        min_age_hours: Optional[int] = None,
        limit: int = 50,
    ) -> JSONDict:
        params: Dict[str, Any] = {"limit": limit}
        if min_age_hours is not None:
            params["min_age_hours"] = min_age_hours
        return await self._transport.request(
            method="GET", path="/outcomes/pending/list", params=params
        )

    async def analytics(
        self,
        *,
        domain: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {}
        if domain:
            params["domain"] = domain
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        return await self._transport.request(
            method="GET", path="/outcomes/analytics/summary", params=params
        )

    async def taxonomy(self) -> JSONDict:
        return await self._transport.request(
            method="GET", path="/outcomes/taxonomy"
        )

    async def recommendation_quality(
        self,
        *,
        domain: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
    ) -> JSONDict:
        """Recommendation quality analytics: follow rate, quadrants, by_domain, examples."""
        params: Dict[str, Any] = {}
        if domain:
            params["domain"] = domain
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        return await self._transport.request(
            method="GET", path="/outcomes/analytics/recommendation-quality", params=params
        )
