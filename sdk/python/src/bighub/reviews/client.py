from __future__ import annotations

from typing import Any, Optional

from ..decisions.types import Decision
from ..protocols import AsyncTransportProtocol, SyncTransportProtocol
from ..types import JSONDict


class ReviewsAPI:
    """Human review queue for decisions that should not run autonomously."""

    def __init__(self, transport: SyncTransportProtocol) -> None:
        self._transport = transport

    def list(self, *, status: str = "pending", limit: Optional[int] = None) -> list[JSONDict]:
        params: JSONDict = {"status": status}
        if limit is not None:
            params["limit"] = limit
        return self._transport.request(method="GET", path="/approvals", params=params)  # type: ignore[return-value]

    def request(
        self,
        decision: Decision | str,
        *,
        reason: Optional[str] = None,
        modified_action: Optional[str] = None,
        better_action: Optional[str] = None,
    ) -> JSONDict:
        return self.create_from_decision(decision, reason=reason, modified_action=modified_action or better_action)

    def create_from_decision(
        self,
        decision: Decision | str,
        *,
        reason: Optional[str] = None,
        modified_action: Optional[str] = None,
    ) -> JSONDict:
        request_id = decision.request_id if isinstance(decision, Decision) else str(decision)
        pending = self.list(status="pending")
        for item in pending:
            if str(item.get("request_id")) == request_id or str(item.get("validation_id")) == request_id:
                if reason or modified_action:
                    item = dict(item)
                    item["review_context"] = {"reason": reason, "modified_action": modified_action}
                return item
        return {
            "request_id": request_id,
            "status": "pending",
            "review_context": {"reason": reason, "modified_action": modified_action},
        }

    def resolve(
        self,
        request_id: str,
        *,
        decision: str,
        reason: Optional[str] = None,
        modified_action: Optional[str] = None,
        better_action: Optional[str] = None,
    ) -> JSONDict:
        if decision not in {"approved", "denied", "modified"}:
            raise ValueError("decision must be 'approved', 'denied', or 'modified'")
        resolution = "approved" if decision == "modified" else decision
        body: JSONDict = {"resolution": resolution}
        if reason:
            body["comment"] = reason
        action_override = modified_action or better_action
        if action_override is not None:
            body["better_action"] = action_override
            body["modified_action"] = action_override
            body["review_decision"] = "modified"
        return self._transport.request(
            method="POST",
            path=f"/approvals/{request_id}/resolve",
            json_body=body,
        )

    def approve(self, request_id: str, *, reason: Optional[str] = None, modified_action: Optional[str] = None) -> JSONDict:
        return self.resolve(request_id, decision="modified" if modified_action else "approved", reason=reason, modified_action=modified_action)

    def deny(self, request_id: str, *, reason: Optional[str] = None) -> JSONDict:
        return self.resolve(request_id, decision="denied", reason=reason)


class AsyncReviewsAPI:
    """Async human review queue."""

    def __init__(self, transport: AsyncTransportProtocol) -> None:
        self._transport = transport

    async def list(self, *, status: str = "pending", limit: Optional[int] = None) -> list[JSONDict]:
        params: JSONDict = {"status": status}
        if limit is not None:
            params["limit"] = limit
        return await self._transport.request(method="GET", path="/approvals", params=params)  # type: ignore[return-value]

    async def request(
        self,
        decision: Decision | str,
        *,
        reason: Optional[str] = None,
        modified_action: Optional[str] = None,
        better_action: Optional[str] = None,
    ) -> JSONDict:
        return await self.create_from_decision(decision, reason=reason, modified_action=modified_action or better_action)

    async def create_from_decision(
        self,
        decision: Decision | str,
        *,
        reason: Optional[str] = None,
        modified_action: Optional[str] = None,
    ) -> JSONDict:
        request_id = decision.request_id if isinstance(decision, Decision) else str(decision)
        pending = await self.list(status="pending")
        for item in pending:
            if str(item.get("request_id")) == request_id or str(item.get("validation_id")) == request_id:
                if reason or modified_action:
                    item = dict(item)
                    item["review_context"] = {"reason": reason, "modified_action": modified_action}
                return item
        return {
            "request_id": request_id,
            "status": "pending",
            "review_context": {"reason": reason, "modified_action": modified_action},
        }

    async def resolve(
        self,
        request_id: str,
        *,
        decision: str,
        reason: Optional[str] = None,
        modified_action: Optional[str] = None,
        better_action: Optional[str] = None,
    ) -> JSONDict:
        if decision not in {"approved", "denied", "modified"}:
            raise ValueError("decision must be 'approved', 'denied', or 'modified'")
        resolution = "approved" if decision == "modified" else decision
        body: JSONDict = {"resolution": resolution}
        if reason:
            body["comment"] = reason
        action_override = modified_action or better_action
        if action_override is not None:
            body["better_action"] = action_override
            body["modified_action"] = action_override
            body["review_decision"] = "modified"
        return await self._transport.request(
            method="POST",
            path=f"/approvals/{request_id}/resolve",
            json_body=body,
        )

    async def approve(self, request_id: str, *, reason: Optional[str] = None, modified_action: Optional[str] = None) -> JSONDict:
        return await self.resolve(request_id, decision="modified" if modified_action else "approved", reason=reason, modified_action=modified_action)

    async def deny(self, request_id: str, *, reason: Optional[str] = None) -> JSONDict:
        return await self.resolve(request_id, decision="denied", reason=reason)
