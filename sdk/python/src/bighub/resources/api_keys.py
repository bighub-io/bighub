from __future__ import annotations

from typing import Dict, Optional, overload

from ..models import APIKeyCreateModel, to_payload
from ..protocols import AsyncTransportProtocol, SyncTransportProtocol
from ..types import APIKeyCreateRequest, APIKeyCreateResponse, JSONDict


class APIKeysAPI:
    """Sync API for API key lifecycle management."""

    def __init__(self, transport: SyncTransportProtocol) -> None:
        self._transport = transport

    @overload
    def create(self, payload: APIKeyCreateRequest) -> APIKeyCreateResponse:
        ...

    @overload
    def create(self, payload: APIKeyCreateModel) -> APIKeyCreateResponse:
        ...

    def create(self, payload: APIKeyCreateRequest | APIKeyCreateModel) -> APIKeyCreateResponse:
        return self._transport.request(method="POST", path="/api-keys", json_body=to_payload(payload))

    def list(self, *, include_revoked: bool = False) -> JSONDict:
        return self._transport.request(
            method="GET",
            path="/api-keys",
            params={"include_revoked": include_revoked},
        )

    def delete(self, key_id: str, *, reason: Optional[str] = None) -> JSONDict:
        json_body = {"reason": reason} if reason is not None else None
        return self._transport.request(method="DELETE", path=f"/api-keys/{key_id}", json_body=json_body)

    def revoke(self, key_id: str, *, reason: Optional[str] = None) -> JSONDict:
        return self.delete(key_id, reason=reason)

    def rotate(self, key_id: str) -> JSONDict:
        return self._transport.request(method="POST", path=f"/api-keys/{key_id}/rotate")

    def validate(self, api_key: str) -> JSONDict:
        return self._transport.request(
            method="GET",
            path="/api-keys/validate",
            params={"api_key": api_key},
            headers={"X-API-Key": api_key},
        )

    def scopes(self) -> JSONDict:
        return self._transport.request(method="GET", path="/api-keys/scopes")


class AsyncAPIKeysAPI:
    """Async API for API key lifecycle management."""

    def __init__(self, transport: AsyncTransportProtocol) -> None:
        self._transport = transport

    @overload
    async def create(self, payload: APIKeyCreateRequest) -> APIKeyCreateResponse:
        ...

    @overload
    async def create(self, payload: APIKeyCreateModel) -> APIKeyCreateResponse:
        ...

    async def create(self, payload: APIKeyCreateRequest | APIKeyCreateModel) -> APIKeyCreateResponse:
        return await self._transport.request(method="POST", path="/api-keys", json_body=to_payload(payload))

    async def list(self, *, include_revoked: bool = False) -> JSONDict:
        return await self._transport.request(
            method="GET",
            path="/api-keys",
            params={"include_revoked": include_revoked},
        )

    async def delete(self, key_id: str, *, reason: Optional[str] = None) -> JSONDict:
        json_body = {"reason": reason} if reason is not None else None
        return await self._transport.request(method="DELETE", path=f"/api-keys/{key_id}", json_body=json_body)

    async def revoke(self, key_id: str, *, reason: Optional[str] = None) -> JSONDict:
        return await self.delete(key_id, reason=reason)

    async def rotate(self, key_id: str) -> JSONDict:
        return await self._transport.request(method="POST", path=f"/api-keys/{key_id}/rotate")

    async def validate(self, api_key: str) -> JSONDict:
        return await self._transport.request(
            method="GET",
            path="/api-keys/validate",
            params={"api_key": api_key},
            headers={"X-API-Key": api_key},
        )

    async def scopes(self) -> JSONDict:
        return await self._transport.request(method="GET", path="/api-keys/scopes")
