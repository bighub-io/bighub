from __future__ import annotations

from typing import Optional

from ..protocols import AsyncTransportProtocol, SyncTransportProtocol
from ..types import JSONDict


class _SystemContextAPI:
    def __init__(self, transport: SyncTransportProtocol, system: str) -> None:
        self._transport = transport
        self.system = system

    def context(self, **kwargs: object) -> JSONDict:
        if self.system == "okta":
            user_login = str(kwargs.get("user_login") or kwargs.get("user") or "")
            if user_login:
                return self._transport.request(method="GET", path=f"/integrations/okta/user/{user_login}")
            return self._transport.request(method="GET", path="/integrations/okta/connection")
        if self.system == "slack":
            return self._transport.request(method="GET", path="/integrations/slack/connection")
        raise NotImplementedError(f"{self.system} system context is not exposed by the current BIGHUB backend yet.")


class _AsyncSystemContextAPI:
    def __init__(self, transport: AsyncTransportProtocol, system: str) -> None:
        self._transport = transport
        self.system = system

    async def context(self, **kwargs: object) -> JSONDict:
        if self.system == "okta":
            user_login = str(kwargs.get("user_login") or kwargs.get("user") or "")
            if user_login:
                return await self._transport.request(method="GET", path=f"/integrations/okta/user/{user_login}")
            return await self._transport.request(method="GET", path="/integrations/okta/connection")
        if self.system == "slack":
            return await self._transport.request(method="GET", path="/integrations/slack/connection")
        raise NotImplementedError(f"{self.system} system context is not exposed by the current BIGHUB backend yet.")


class SystemsAPI:
    """System context surface for IT decisions."""

    def __init__(self, transport: SyncTransportProtocol) -> None:
        self._transport = transport
        self.okta = _SystemContextAPI(transport, "okta")
        self.slack = _SystemContextAPI(transport, "slack")
        self.github = _SystemContextAPI(transport, "github")
        self.datadog = _SystemContextAPI(transport, "datadog")
        self.sentry = _SystemContextAPI(transport, "sentry")

    def world_state(
        self,
        *,
        limit: int = 100,
        freshness_minutes: int = 30,
        in_flight_minutes: int = 60,
    ) -> JSONDict:
        return self._transport.request(
            method="GET",
            path="/world-state/operational",
            params={
                "limit": limit,
                "freshness_minutes": freshness_minutes,
                "in_flight_minutes": in_flight_minutes,
            },
        )

    def context(self, system: str, **kwargs: object) -> JSONDict:
        return _SystemContextAPI(self._transport, system).context(**kwargs)

    def okta_context(self, **kwargs: object) -> JSONDict:
        return self.okta.context(**kwargs)

    def slack_context(self, **kwargs: object) -> JSONDict:
        return self.slack.context(**kwargs)

    def github_context(self, **kwargs: object) -> JSONDict:
        return self.github.context(**kwargs)

    def datadog_context(self, **kwargs: object) -> JSONDict:
        return self.datadog.context(**kwargs)

    def sentry_context(self, **kwargs: object) -> JSONDict:
        return self.sentry.context(**kwargs)


class AsyncSystemsAPI:
    """Async system context surface for IT decisions."""

    def __init__(self, transport: AsyncTransportProtocol) -> None:
        self._transport = transport
        self.okta = _AsyncSystemContextAPI(transport, "okta")
        self.slack = _AsyncSystemContextAPI(transport, "slack")
        self.github = _AsyncSystemContextAPI(transport, "github")
        self.datadog = _AsyncSystemContextAPI(transport, "datadog")
        self.sentry = _AsyncSystemContextAPI(transport, "sentry")

    async def world_state(
        self,
        *,
        limit: int = 100,
        freshness_minutes: int = 30,
        in_flight_minutes: int = 60,
    ) -> JSONDict:
        return await self._transport.request(
            method="GET",
            path="/world-state/operational",
            params={
                "limit": limit,
                "freshness_minutes": freshness_minutes,
                "in_flight_minutes": in_flight_minutes,
            },
        )

    async def context(self, system: str, **kwargs: object) -> JSONDict:
        return await _AsyncSystemContextAPI(self._transport, system).context(**kwargs)

    async def okta_context(self, **kwargs: object) -> JSONDict:
        return await self.okta.context(**kwargs)

    async def slack_context(self, **kwargs: object) -> JSONDict:
        return await self.slack.context(**kwargs)

    async def github_context(self, **kwargs: object) -> JSONDict:
        return await self.github.context(**kwargs)

    async def datadog_context(self, **kwargs: object) -> JSONDict:
        return await self.datadog.context(**kwargs)

    async def sentry_context(self, **kwargs: object) -> JSONDict:
        return await self.sentry.context(**kwargs)
