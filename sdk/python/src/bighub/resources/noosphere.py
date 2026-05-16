"""Federated Noosphere SDK resource.

Read-only access to BIGHUB's cross-organization civilizational learning view.
The federated layer never returns any other org's identifiers, payloads, or
transition ids. Patterns are aggregated, anonymized, and only published
after k-anonymity filtering.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..types import (
    FederatedApplicabilityReportResponse,
    FederatedApplicabilityVerdictResponse,
    FederatedBreachPatternDict,
    FederatedContributionResponse,
    FederatedDisagreementPatternDict,
    FederatedInvariantPatternDict,
    FederatedNoosphereSnapshotResponse,
)


_Sync = Any
_Async = Any


class NoosphereAPI:
    """Sync access to ``/federated-noosphere/*`` endpoints."""

    def __init__(self, transport: _Sync) -> None:
        self._transport = transport

    def contribute(self) -> FederatedContributionResponse:
        """Refresh this org's structurally-abstract contribution to the noosphere."""

        return self._transport.request(method="POST", path="/federated-noosphere/contribute")

    def snapshot(self) -> FederatedNoosphereSnapshotResponse:
        """Read the latest aggregated cross-org snapshot."""

        return self._transport.request(method="GET", path="/federated-noosphere/snapshot")

    def refresh(
        self,
        *,
        k_anonymity_threshold: Optional[int] = None,
        min_total_support: Optional[int] = None,
    ) -> FederatedNoosphereSnapshotResponse:
        params: Dict[str, Any] = {}
        if k_anonymity_threshold is not None:
            params["k_anonymity_threshold"] = k_anonymity_threshold
        if min_total_support is not None:
            params["min_total_support"] = min_total_support
        return self._transport.request(
            method="POST", path="/federated-noosphere/refresh", params=params
        )

    def invariant_patterns(
        self,
        *,
        invariant_type: Optional[str] = None,
        domain: Optional[str] = None,
        min_contributing_orgs: Optional[int] = None,
    ) -> List[FederatedInvariantPatternDict]:
        params: Dict[str, Any] = {}
        if invariant_type:
            params["invariant_type"] = invariant_type
        if domain:
            params["domain"] = domain
        if min_contributing_orgs is not None:
            params["min_contributing_orgs"] = min_contributing_orgs
        return self._transport.request(
            method="GET",
            path="/federated-noosphere/invariant-patterns",
            params=params,
        )

    def disagreement_patterns(
        self,
        *,
        disagreement_type: Optional[str] = None,
        civilizational_winner: Optional[str] = None,
        min_contributing_orgs: Optional[int] = None,
    ) -> List[FederatedDisagreementPatternDict]:
        params: Dict[str, Any] = {}
        if disagreement_type:
            params["disagreement_type"] = disagreement_type
        if civilizational_winner:
            params["civilizational_winner"] = civilizational_winner
        if min_contributing_orgs is not None:
            params["min_contributing_orgs"] = min_contributing_orgs
        return self._transport.request(
            method="GET",
            path="/federated-noosphere/disagreement-patterns",
            params=params,
        )

    def breach_patterns(
        self,
        *,
        promise_type: Optional[str] = None,
        min_contributing_orgs: Optional[int] = None,
    ) -> List[FederatedBreachPatternDict]:
        params: Dict[str, Any] = {}
        if promise_type:
            params["promise_type"] = promise_type
        if min_contributing_orgs is not None:
            params["min_contributing_orgs"] = min_contributing_orgs
        return self._transport.request(
            method="GET",
            path="/federated-noosphere/breach-patterns",
            params=params,
        )

    def invariant_applicability(self, pattern_id: str) -> FederatedApplicabilityVerdictResponse:
        return self._transport.request(
            method="GET",
            path=f"/federated-noosphere/applicability/invariant/{pattern_id}",
        )

    def disagreement_applicability(self, pattern_id: str) -> FederatedApplicabilityVerdictResponse:
        return self._transport.request(
            method="GET",
            path=f"/federated-noosphere/applicability/disagreement/{pattern_id}",
        )

    def applicability_report(self) -> FederatedApplicabilityReportResponse:
        return self._transport.request(
            method="GET",
            path="/federated-noosphere/applicability",
        )


class AsyncNoosphereAPI:
    """Async mirror of :class:`NoosphereAPI`."""

    def __init__(self, transport: _Async) -> None:
        self._transport = transport

    async def contribute(self) -> FederatedContributionResponse:
        return await self._transport.request(
            method="POST", path="/federated-noosphere/contribute"
        )

    async def snapshot(self) -> FederatedNoosphereSnapshotResponse:
        return await self._transport.request(
            method="GET", path="/federated-noosphere/snapshot"
        )

    async def refresh(
        self,
        *,
        k_anonymity_threshold: Optional[int] = None,
        min_total_support: Optional[int] = None,
    ) -> FederatedNoosphereSnapshotResponse:
        params: Dict[str, Any] = {}
        if k_anonymity_threshold is not None:
            params["k_anonymity_threshold"] = k_anonymity_threshold
        if min_total_support is not None:
            params["min_total_support"] = min_total_support
        return await self._transport.request(
            method="POST", path="/federated-noosphere/refresh", params=params
        )

    async def invariant_patterns(
        self,
        *,
        invariant_type: Optional[str] = None,
        domain: Optional[str] = None,
        min_contributing_orgs: Optional[int] = None,
    ) -> List[FederatedInvariantPatternDict]:
        params: Dict[str, Any] = {}
        if invariant_type:
            params["invariant_type"] = invariant_type
        if domain:
            params["domain"] = domain
        if min_contributing_orgs is not None:
            params["min_contributing_orgs"] = min_contributing_orgs
        return await self._transport.request(
            method="GET",
            path="/federated-noosphere/invariant-patterns",
            params=params,
        )

    async def disagreement_patterns(
        self,
        *,
        disagreement_type: Optional[str] = None,
        civilizational_winner: Optional[str] = None,
        min_contributing_orgs: Optional[int] = None,
    ) -> List[FederatedDisagreementPatternDict]:
        params: Dict[str, Any] = {}
        if disagreement_type:
            params["disagreement_type"] = disagreement_type
        if civilizational_winner:
            params["civilizational_winner"] = civilizational_winner
        if min_contributing_orgs is not None:
            params["min_contributing_orgs"] = min_contributing_orgs
        return await self._transport.request(
            method="GET",
            path="/federated-noosphere/disagreement-patterns",
            params=params,
        )

    async def breach_patterns(
        self,
        *,
        promise_type: Optional[str] = None,
        min_contributing_orgs: Optional[int] = None,
    ) -> List[FederatedBreachPatternDict]:
        params: Dict[str, Any] = {}
        if promise_type:
            params["promise_type"] = promise_type
        if min_contributing_orgs is not None:
            params["min_contributing_orgs"] = min_contributing_orgs
        return await self._transport.request(
            method="GET",
            path="/federated-noosphere/breach-patterns",
            params=params,
        )

    async def invariant_applicability(self, pattern_id: str) -> FederatedApplicabilityVerdictResponse:
        return await self._transport.request(
            method="GET",
            path=f"/federated-noosphere/applicability/invariant/{pattern_id}",
        )

    async def disagreement_applicability(self, pattern_id: str) -> FederatedApplicabilityVerdictResponse:
        return await self._transport.request(
            method="GET",
            path=f"/federated-noosphere/applicability/disagreement/{pattern_id}",
        )

    async def applicability_report(self) -> FederatedApplicabilityReportResponse:
        return await self._transport.request(
            method="GET",
            path="/federated-noosphere/applicability",
        )


__all__ = ["NoosphereAPI", "AsyncNoosphereAPI"]
