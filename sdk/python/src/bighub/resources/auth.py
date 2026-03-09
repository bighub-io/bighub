from __future__ import annotations

from typing import Dict, overload

from ..models import AuthCredentialsModel, to_payload
from ..protocols import AsyncTransportProtocol, SyncTransportProtocol
from ..types import AuthTokens, JSONDict


class AuthAPI:
    """Sync API for authentication token lifecycle."""

    def __init__(self, transport: SyncTransportProtocol) -> None:
        self._transport = transport

    @overload
    def signup(self, payload: JSONDict) -> AuthTokens:
        ...

    @overload
    def signup(self, payload: AuthCredentialsModel) -> AuthTokens:
        ...

    def signup(self, payload: JSONDict | AuthCredentialsModel) -> AuthTokens:
        """Create a user and issue access/refresh tokens."""
        return self._transport.request(method="POST", path="/auth/signup", json_body=to_payload(payload))

    @overload
    def login(self, payload: JSONDict) -> AuthTokens:
        ...

    @overload
    def login(self, payload: AuthCredentialsModel) -> AuthTokens:
        ...

    def login(self, payload: JSONDict | AuthCredentialsModel) -> AuthTokens:
        """Authenticate a user and issue access/refresh tokens."""
        return self._transport.request(method="POST", path="/auth/login", json_body=to_payload(payload))

    def refresh(self, refresh_token: str) -> AuthTokens:
        """Rotate tokens using a refresh token."""
        return self._transport.request(
            method="POST",
            path="/auth/refresh",
            json_body={"refresh_token": refresh_token},
        )

    def logout(self, refresh_token: str) -> JSONDict:
        """Invalidate a refresh token."""
        return self._transport.request(
            method="POST",
            path="/auth/logout",
            json_body={"refresh_token": refresh_token},
        )


class AsyncAuthAPI:
    """Async API for authentication token lifecycle."""

    def __init__(self, transport: AsyncTransportProtocol) -> None:
        self._transport = transport

    @overload
    async def signup(self, payload: JSONDict) -> AuthTokens:
        ...

    @overload
    async def signup(self, payload: AuthCredentialsModel) -> AuthTokens:
        ...

    async def signup(self, payload: JSONDict | AuthCredentialsModel) -> AuthTokens:
        """Create a user and issue access/refresh tokens."""
        return await self._transport.request(method="POST", path="/auth/signup", json_body=to_payload(payload))

    @overload
    async def login(self, payload: JSONDict) -> AuthTokens:
        ...

    @overload
    async def login(self, payload: AuthCredentialsModel) -> AuthTokens:
        ...

    async def login(self, payload: JSONDict | AuthCredentialsModel) -> AuthTokens:
        """Authenticate a user and issue access/refresh tokens."""
        return await self._transport.request(method="POST", path="/auth/login", json_body=to_payload(payload))

    async def refresh(self, refresh_token: str) -> AuthTokens:
        """Rotate tokens using a refresh token."""
        return await self._transport.request(
            method="POST",
            path="/auth/refresh",
            json_body={"refresh_token": refresh_token},
        )

    async def logout(self, refresh_token: str) -> JSONDict:
        """Invalidate a refresh token."""
        return await self._transport.request(
            method="POST",
            path="/auth/logout",
            json_body={"refresh_token": refresh_token},
        )
