from __future__ import annotations

from typing import Dict, List, Optional, overload

from ..models import RuleCreateModel, RuleUpdateModel, RuleValidateModel, to_payload
from ..protocols import AsyncTransportProtocol, SyncTransportProtocol
from ..types import (
    DomainInfo,
    JSONDict,
    RuleCreateRequest,
    RuleResponse,
    RuleUpdateRequest,
    RuleValidateRequest,
)


class RulesAPI:
    """Sync API for rule lifecycle and governance endpoints."""

    def __init__(self, transport: SyncTransportProtocol) -> None:
        self._transport = transport

    @overload
    def create(self, payload: RuleCreateRequest, *, idempotency_key: Optional[str] = None) -> RuleResponse:
        ...

    @overload
    def create(self, payload: RuleCreateModel, *, idempotency_key: Optional[str] = None) -> RuleResponse:
        ...

    def create(
        self,
        payload: RuleCreateRequest | RuleCreateModel,
        *,
        idempotency_key: Optional[str] = None,
    ) -> RuleResponse:
        return self._transport.request(
            method="POST",
            path="/rules",
            json_body=to_payload(payload),
            idempotency_key=idempotency_key,
        )

    def list(
        self,
        *,
        status: Optional[str] = None,
        domain: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[RuleResponse]:
        params: Dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if domain is not None:
            params["domain"] = domain
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return self._transport.request(method="GET", path="/rules", params=params)

    def get(self, rule_id: str) -> RuleResponse:
        return self._transport.request(method="GET", path=f"/rules/{rule_id}")

    @overload
    def update(
        self,
        rule_id: str,
        payload: RuleCreateRequest,
        *,
        idempotency_key: Optional[str] = None,
    ) -> RuleResponse:
        ...

    @overload
    def update(
        self,
        rule_id: str,
        payload: RuleCreateModel,
        *,
        idempotency_key: Optional[str] = None,
    ) -> RuleResponse:
        ...

    @overload
    def update(
        self,
        rule_id: str,
        payload: RuleUpdateRequest,
        *,
        idempotency_key: Optional[str] = None,
    ) -> RuleResponse:
        ...

    @overload
    def update(
        self,
        rule_id: str,
        payload: RuleUpdateModel,
        *,
        idempotency_key: Optional[str] = None,
    ) -> RuleResponse:
        ...

    def update(
        self,
        rule_id: str,
        payload: RuleCreateRequest | RuleCreateModel | RuleUpdateRequest | RuleUpdateModel,
        *,
        idempotency_key: Optional[str] = None,
    ) -> RuleResponse:
        return self._transport.request(
            method="PATCH",
            path=f"/rules/{rule_id}",
            json_body=to_payload(payload),
            idempotency_key=idempotency_key,
        )

    def delete(self, rule_id: str, *, idempotency_key: Optional[str] = None) -> JSONDict:
        return self._transport.request(
            method="DELETE",
            path=f"/rules/{rule_id}",
            idempotency_key=idempotency_key,
        )

    def pause(self, rule_id: str, *, idempotency_key: Optional[str] = None) -> JSONDict:
        return self._transport.request(
            method="POST",
            path=f"/rules/{rule_id}/pause",
            idempotency_key=idempotency_key,
        )

    def resume(self, rule_id: str, *, idempotency_key: Optional[str] = None) -> JSONDict:
        return self._transport.request(
            method="POST",
            path=f"/rules/{rule_id}/resume",
            idempotency_key=idempotency_key,
        )

    @overload
    def dry_run(self, payload: RuleCreateRequest) -> JSONDict:
        ...

    @overload
    def dry_run(self, payload: RuleCreateModel) -> JSONDict:
        ...

    def dry_run(self, payload: RuleCreateRequest | RuleCreateModel) -> JSONDict:
        return self._transport.request(method="POST", path="/rules/dry-run", json_body=to_payload(payload))

    @overload
    def validate(self, payload: RuleValidateRequest) -> JSONDict:
        ...

    @overload
    def validate(self, payload: RuleValidateModel) -> JSONDict:
        ...

    def validate(self, payload: RuleValidateRequest | RuleValidateModel) -> JSONDict:
        return self._transport.request(method="POST", path="/rules/validate", json_body=to_payload(payload))

    @overload
    def validate_dry_run(self, payload: RuleValidateRequest) -> JSONDict:
        ...

    @overload
    def validate_dry_run(self, payload: RuleValidateModel) -> JSONDict:
        ...

    def validate_dry_run(self, payload: RuleValidateRequest | RuleValidateModel) -> JSONDict:
        return self._transport.request(method="POST", path="/rules/validate/dry-run", json_body=to_payload(payload))

    def domains(self) -> List[DomainInfo]:
        return self._transport.request(method="GET", path="/rules/domains")

    def versions(self, rule_id: str, *, limit: Optional[int] = None) -> List[JSONDict]:
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        return self._transport.request(method="GET", path=f"/rules/{rule_id}/versions", params=params)

    def purge_idempotency(
        self,
        *,
        only_expired: bool = True,
        older_than_hours: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {"only_expired": only_expired}
        if older_than_hours is not None:
            params["older_than_hours"] = older_than_hours
        if limit is not None:
            params["limit"] = limit
        return self._transport.request(
            method="POST",
            path="/rules/admin/idempotency/purge",
            params=params,
        )

    def apply_patch(
        self,
        rule_id: str,
        *,
        patch: JSONDict | List[JSONDict],
        preview: bool = True,
        reason: Optional[str] = None,
        if_match_version: Optional[int] = None,
        idempotency_key: Optional[str] = None,
        if_match: Optional[str] = None,
    ) -> JSONDict:
        patch_ops = patch.get("ops") if isinstance(patch, dict) else patch
        if not isinstance(patch_ops, list):
            raise ValueError("patch must be a JSON Patch ops list or {'format': 'json_patch', 'ops': [...]} object")
        payload: JSONDict = {"patch": patch_ops, "preview": preview}
        if reason is not None:
            payload["reason"] = reason
        if if_match_version is not None:
            payload["if_match_version"] = if_match_version
        headers: Dict[str, str] = {}
        if if_match is not None:
            headers["If-Match"] = if_match
        return self._transport.request(
            method="POST",
            path=f"/rules/{rule_id}/apply_patch",
            json_body=payload,
            idempotency_key=idempotency_key,
            headers=headers or None,
        )


class AsyncRulesAPI:
    """Async API for rule lifecycle and governance endpoints."""

    def __init__(self, transport: AsyncTransportProtocol) -> None:
        self._transport = transport

    @overload
    async def create(self, payload: RuleCreateRequest, *, idempotency_key: Optional[str] = None) -> RuleResponse:
        ...

    @overload
    async def create(self, payload: RuleCreateModel, *, idempotency_key: Optional[str] = None) -> RuleResponse:
        ...

    async def create(
        self,
        payload: RuleCreateRequest | RuleCreateModel,
        *,
        idempotency_key: Optional[str] = None,
    ) -> RuleResponse:
        return await self._transport.request(
            method="POST",
            path="/rules",
            json_body=to_payload(payload),
            idempotency_key=idempotency_key,
        )

    async def list(
        self,
        *,
        status: Optional[str] = None,
        domain: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[RuleResponse]:
        params: Dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if domain is not None:
            params["domain"] = domain
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return await self._transport.request(method="GET", path="/rules", params=params)

    async def get(self, rule_id: str) -> RuleResponse:
        return await self._transport.request(method="GET", path=f"/rules/{rule_id}")

    @overload
    async def update(
        self,
        rule_id: str,
        payload: RuleCreateRequest,
        *,
        idempotency_key: Optional[str] = None,
    ) -> RuleResponse:
        ...

    @overload
    async def update(
        self,
        rule_id: str,
        payload: RuleCreateModel,
        *,
        idempotency_key: Optional[str] = None,
    ) -> RuleResponse:
        ...

    @overload
    async def update(
        self,
        rule_id: str,
        payload: RuleUpdateRequest,
        *,
        idempotency_key: Optional[str] = None,
    ) -> RuleResponse:
        ...

    @overload
    async def update(
        self,
        rule_id: str,
        payload: RuleUpdateModel,
        *,
        idempotency_key: Optional[str] = None,
    ) -> RuleResponse:
        ...

    async def update(
        self,
        rule_id: str,
        payload: RuleCreateRequest | RuleCreateModel | RuleUpdateRequest | RuleUpdateModel,
        *,
        idempotency_key: Optional[str] = None,
    ) -> RuleResponse:
        return await self._transport.request(
            method="PATCH",
            path=f"/rules/{rule_id}",
            json_body=to_payload(payload),
            idempotency_key=idempotency_key,
        )

    async def delete(self, rule_id: str, *, idempotency_key: Optional[str] = None) -> JSONDict:
        return await self._transport.request(
            method="DELETE",
            path=f"/rules/{rule_id}",
            idempotency_key=idempotency_key,
        )

    async def pause(self, rule_id: str, *, idempotency_key: Optional[str] = None) -> JSONDict:
        return await self._transport.request(
            method="POST",
            path=f"/rules/{rule_id}/pause",
            idempotency_key=idempotency_key,
        )

    async def resume(self, rule_id: str, *, idempotency_key: Optional[str] = None) -> JSONDict:
        return await self._transport.request(
            method="POST",
            path=f"/rules/{rule_id}/resume",
            idempotency_key=idempotency_key,
        )

    @overload
    async def dry_run(self, payload: RuleCreateRequest) -> JSONDict:
        ...

    @overload
    async def dry_run(self, payload: RuleCreateModel) -> JSONDict:
        ...

    async def dry_run(self, payload: RuleCreateRequest | RuleCreateModel) -> JSONDict:
        return await self._transport.request(method="POST", path="/rules/dry-run", json_body=to_payload(payload))

    @overload
    async def validate(self, payload: RuleValidateRequest) -> JSONDict:
        ...

    @overload
    async def validate(self, payload: RuleValidateModel) -> JSONDict:
        ...

    async def validate(self, payload: RuleValidateRequest | RuleValidateModel) -> JSONDict:
        return await self._transport.request(method="POST", path="/rules/validate", json_body=to_payload(payload))

    @overload
    async def validate_dry_run(self, payload: RuleValidateRequest) -> JSONDict:
        ...

    @overload
    async def validate_dry_run(self, payload: RuleValidateModel) -> JSONDict:
        ...

    async def validate_dry_run(self, payload: RuleValidateRequest | RuleValidateModel) -> JSONDict:
        return await self._transport.request(method="POST", path="/rules/validate/dry-run", json_body=to_payload(payload))

    async def domains(self) -> List[DomainInfo]:
        return await self._transport.request(method="GET", path="/rules/domains")

    async def versions(self, rule_id: str, *, limit: Optional[int] = None) -> List[JSONDict]:
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        return await self._transport.request(method="GET", path=f"/rules/{rule_id}/versions", params=params)

    async def purge_idempotency(
        self,
        *,
        only_expired: bool = True,
        older_than_hours: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> JSONDict:
        params: Dict[str, Any] = {"only_expired": only_expired}
        if older_than_hours is not None:
            params["older_than_hours"] = older_than_hours
        if limit is not None:
            params["limit"] = limit
        return await self._transport.request(
            method="POST",
            path="/rules/admin/idempotency/purge",
            params=params,
        )

    async def apply_patch(
        self,
        rule_id: str,
        *,
        patch: JSONDict | List[JSONDict],
        preview: bool = True,
        reason: Optional[str] = None,
        if_match_version: Optional[int] = None,
        idempotency_key: Optional[str] = None,
        if_match: Optional[str] = None,
    ) -> JSONDict:
        patch_ops = patch.get("ops") if isinstance(patch, dict) else patch
        if not isinstance(patch_ops, list):
            raise ValueError("patch must be a JSON Patch ops list or {'format': 'json_patch', 'ops': [...]} object")
        payload: JSONDict = {"patch": patch_ops, "preview": preview}
        if reason is not None:
            payload["reason"] = reason
        if if_match_version is not None:
            payload["if_match_version"] = if_match_version
        headers: Dict[str, str] = {}
        if if_match is not None:
            headers["If-Match"] = if_match
        return await self._transport.request(
            method="POST",
            path=f"/rules/{rule_id}/apply_patch",
            json_body=payload,
            idempotency_key=idempotency_key,
            headers=headers or None,
        )
