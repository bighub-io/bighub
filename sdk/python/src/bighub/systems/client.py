from __future__ import annotations

from typing import Any, Dict, Optional

from ..protocols import AsyncTransportProtocol, SyncTransportProtocol
from ..types import (
    JSONDict,
    SystemConnectionResponse,
    SystemPollHistoryResponse,
    SystemPollMetricsResponse,
    SystemPollScheduleResponse,
    SystemPollStatusResponse,
)


SYSTEM_PROVIDERS = (
    "github",
    "sentry",
    "datadog",
    "aws_cloudtrail",
    "terraform",
    "kubernetes",
    "argocd",
    "gitlab",
    "jenkins",
    "azure",
    "prometheus",
    "grafana",
    "openshift",
)

PROVIDER_ALIASES = {
    "github": "github",
    "github-ci": "github",
    "github_ci": "github",
    "sentry": "sentry",
    "datadog": "datadog",
    "aws-cloudtrail": "aws_cloudtrail",
    "aws_cloudtrail": "aws_cloudtrail",
    "cloudtrail": "aws_cloudtrail",
    "terraform": "terraform",
    "terraform-cloud": "terraform",
    "terraform_cloud": "terraform",
    "tfc": "terraform",
    "tfe": "terraform",
    "kubernetes": "kubernetes",
    "k8s": "kubernetes",
    "argocd": "argocd",
    "argo-cd": "argocd",
    "argo_cd": "argocd",
    "gitlab": "gitlab",
    "gitlab-ci": "gitlab",
    "gitlab_ci": "gitlab",
    "jenkins": "jenkins",
    "azure": "azure",
    "prometheus": "prometheus",
    "grafana": "grafana",
    "openshift": "openshift",
    "ocp": "openshift",
}


def _provider(raw: str) -> str:
    provider = PROVIDER_ALIASES.get(str(raw or "").strip().lower())
    if not provider:
        raise ValueError(f"Unsupported BIGHUB system provider: {raw}")
    return provider


def _params(**kwargs: object) -> Dict[str, object]:
    return {key: value for key, value in kwargs.items() if value is not None}


class _SystemContextAPI:
    def __init__(self, transport: SyncTransportProtocol, system: str) -> None:
        self._transport = transport
        self.system = _provider(system) if system not in {"okta", "slack"} else system

    def context(self, **kwargs: object) -> JSONDict:
        if self.system == "okta":
            user_login = str(kwargs.get("user_login") or kwargs.get("user") or "")
            if user_login:
                return self._transport.request(method="GET", path=f"/integrations/okta/user/{user_login}")
            return self._transport.request(method="GET", path="/integrations/okta/connection")
        if self.system == "slack":
            return self._transport.request(method="GET", path="/integrations/slack/connection")
        return self.connection(org_id=kwargs.get("org_id"))

    def connection(self, *, org_id: object = None) -> SystemConnectionResponse:
        return self._transport.request(
            method="GET",
            path=f"/integrations/{self.system}/connection",
            params=_params(org_id=org_id),
        )

    def test(self, config: JSONDict, *, org_id: object = None) -> SystemConnectionResponse:
        return self._transport.request(
            method="POST",
            path=f"/integrations/{self.system}/connection/test",
            params=_params(org_id=org_id),
            json_body=dict(config),
        )

    def save(
        self,
        config: JSONDict,
        *,
        org_id: object = None,
        display_name: Optional[str] = None,
    ) -> SystemConnectionResponse:
        body = dict(config)
        if display_name is not None:
            body["display_name"] = display_name
        return self._transport.request(
            method="PUT",
            path=f"/integrations/{self.system}/connection",
            params=_params(org_id=org_id),
            json_body=body,
        )

    def delete(self, *, org_id: object = None) -> JSONDict:
        return self._transport.request(
            method="DELETE",
            path=f"/integrations/{self.system}/connection",
            params=_params(org_id=org_id),
        )

    def poll(self, *, org_id: object = None) -> JSONDict:
        return self._transport.request(
            method="POST",
            path=f"/integrations/{self.system}/poll",
            params=_params(org_id=org_id),
        )

    def schedule(self, *, org_id: object = None) -> SystemPollScheduleResponse:
        return self._transport.request(
            method="GET",
            path=f"/integrations/{self.system}/poll/schedule",
            params=_params(org_id=org_id),
        )

    def update_schedule(
        self,
        *,
        enabled: bool = True,
        interval_seconds: int = 300,
        max_backoff_seconds: int = 3600,
        org_id: object = None,
    ) -> SystemPollScheduleResponse:
        return self._transport.request(
            method="PUT",
            path=f"/integrations/{self.system}/poll/schedule",
            params=_params(org_id=org_id),
            json_body={
                "enabled": enabled,
                "interval_seconds": interval_seconds,
                "max_backoff_seconds": max_backoff_seconds,
            },
        )

    def history(self, *, limit: int = 50, org_id: object = None) -> SystemPollHistoryResponse:
        return self._transport.request(
            method="GET",
            path=f"/integrations/{self.system}/poll/history",
            params=_params(org_id=org_id, limit=limit),
        )


class _AsyncSystemContextAPI:
    def __init__(self, transport: AsyncTransportProtocol, system: str) -> None:
        self._transport = transport
        self.system = _provider(system) if system not in {"okta", "slack"} else system

    async def context(self, **kwargs: object) -> JSONDict:
        if self.system == "okta":
            user_login = str(kwargs.get("user_login") or kwargs.get("user") or "")
            if user_login:
                return await self._transport.request(method="GET", path=f"/integrations/okta/user/{user_login}")
            return await self._transport.request(method="GET", path="/integrations/okta/connection")
        if self.system == "slack":
            return await self._transport.request(method="GET", path="/integrations/slack/connection")
        return await self.connection(org_id=kwargs.get("org_id"))

    async def connection(self, *, org_id: object = None) -> SystemConnectionResponse:
        return await self._transport.request(
            method="GET",
            path=f"/integrations/{self.system}/connection",
            params=_params(org_id=org_id),
        )

    async def test(self, config: JSONDict, *, org_id: object = None) -> SystemConnectionResponse:
        return await self._transport.request(
            method="POST",
            path=f"/integrations/{self.system}/connection/test",
            params=_params(org_id=org_id),
            json_body=dict(config),
        )

    async def save(
        self,
        config: JSONDict,
        *,
        org_id: object = None,
        display_name: Optional[str] = None,
    ) -> SystemConnectionResponse:
        body = dict(config)
        if display_name is not None:
            body["display_name"] = display_name
        return await self._transport.request(
            method="PUT",
            path=f"/integrations/{self.system}/connection",
            params=_params(org_id=org_id),
            json_body=body,
        )

    async def delete(self, *, org_id: object = None) -> JSONDict:
        return await self._transport.request(
            method="DELETE",
            path=f"/integrations/{self.system}/connection",
            params=_params(org_id=org_id),
        )

    async def poll(self, *, org_id: object = None) -> JSONDict:
        return await self._transport.request(
            method="POST",
            path=f"/integrations/{self.system}/poll",
            params=_params(org_id=org_id),
        )

    async def schedule(self, *, org_id: object = None) -> SystemPollScheduleResponse:
        return await self._transport.request(
            method="GET",
            path=f"/integrations/{self.system}/poll/schedule",
            params=_params(org_id=org_id),
        )

    async def update_schedule(
        self,
        *,
        enabled: bool = True,
        interval_seconds: int = 300,
        max_backoff_seconds: int = 3600,
        org_id: object = None,
    ) -> SystemPollScheduleResponse:
        return await self._transport.request(
            method="PUT",
            path=f"/integrations/{self.system}/poll/schedule",
            params=_params(org_id=org_id),
            json_body={
                "enabled": enabled,
                "interval_seconds": interval_seconds,
                "max_backoff_seconds": max_backoff_seconds,
            },
        )

    async def history(self, *, limit: int = 50, org_id: object = None) -> SystemPollHistoryResponse:
        return await self._transport.request(
            method="GET",
            path=f"/integrations/{self.system}/poll/history",
            params=_params(org_id=org_id, limit=limit),
        )


class SystemsAPI:
    """System context surface for IT decisions."""

    def __init__(self, transport: SyncTransportProtocol) -> None:
        self._transport = transport
        self.okta = _SystemContextAPI(transport, "okta")
        self.slack = _SystemContextAPI(transport, "slack")
        self.github = _SystemContextAPI(transport, "github")
        self.datadog = _SystemContextAPI(transport, "datadog")
        self.sentry = _SystemContextAPI(transport, "sentry")
        self.aws_cloudtrail = _SystemContextAPI(transport, "aws_cloudtrail")
        self.terraform = _SystemContextAPI(transport, "terraform")
        self.kubernetes = _SystemContextAPI(transport, "kubernetes")
        self.argocd = _SystemContextAPI(transport, "argocd")
        self.gitlab = _SystemContextAPI(transport, "gitlab")
        self.jenkins = _SystemContextAPI(transport, "jenkins")
        self.azure = _SystemContextAPI(transport, "azure")
        self.prometheus = _SystemContextAPI(transport, "prometheus")
        self.grafana = _SystemContextAPI(transport, "grafana")
        self.openshift = _SystemContextAPI(transport, "openshift")

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

    def list_connections(self, *, org_id: object = None) -> JSONDict:
        return self._transport.request(method="GET", path="/integrations/connections", params=_params(org_id=org_id))

    def connection(self, provider: str, *, org_id: object = None) -> SystemConnectionResponse:
        return _SystemContextAPI(self._transport, provider).connection(org_id=org_id)

    def test_connection(self, provider: str, config: JSONDict, *, org_id: object = None) -> SystemConnectionResponse:
        return _SystemContextAPI(self._transport, provider).test(config, org_id=org_id)

    def save_connection(
        self,
        provider: str,
        config: JSONDict,
        *,
        org_id: object = None,
        display_name: Optional[str] = None,
    ) -> SystemConnectionResponse:
        return _SystemContextAPI(self._transport, provider).save(config, org_id=org_id, display_name=display_name)

    def delete_connection(self, provider: str, *, org_id: object = None) -> JSONDict:
        return _SystemContextAPI(self._transport, provider).delete(org_id=org_id)

    def poll(self, provider: str, *, org_id: object = None) -> JSONDict:
        return _SystemContextAPI(self._transport, provider).poll(org_id=org_id)

    def poll_schedule(self, provider: str, *, org_id: object = None) -> SystemPollScheduleResponse:
        return _SystemContextAPI(self._transport, provider).schedule(org_id=org_id)

    def update_poll_schedule(
        self,
        provider: str,
        *,
        enabled: bool = True,
        interval_seconds: int = 300,
        max_backoff_seconds: int = 3600,
        org_id: object = None,
    ) -> SystemPollScheduleResponse:
        return _SystemContextAPI(self._transport, provider).update_schedule(
            enabled=enabled,
            interval_seconds=interval_seconds,
            max_backoff_seconds=max_backoff_seconds,
            org_id=org_id,
        )

    def poll_history(self, provider: str, *, limit: int = 50, org_id: object = None) -> SystemPollHistoryResponse:
        return _SystemContextAPI(self._transport, provider).history(limit=limit, org_id=org_id)

    def poll_status(self, *, org_id: object = None) -> SystemPollStatusResponse:
        return self._transport.request(method="GET", path="/integrations/poll/status", params=_params(org_id=org_id))

    def poll_metrics(self, *, org_id: object = None) -> SystemPollMetricsResponse:
        return self._transport.request(method="GET", path="/integrations/poll/metrics", params=_params(org_id=org_id))

    def run_due_polls(self, *, org_id: object = None) -> JSONDict:
        return self._transport.request(method="POST", path="/integrations/poll/run-due", params=_params(org_id=org_id))

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

    def __getattr__(self, name: str) -> Any:
        if name in PROVIDER_ALIASES:
            return _SystemContextAPI(self._transport, name)
        raise AttributeError(name)


class AsyncSystemsAPI:
    """Async system context surface for IT decisions."""

    def __init__(self, transport: AsyncTransportProtocol) -> None:
        self._transport = transport
        self.okta = _AsyncSystemContextAPI(transport, "okta")
        self.slack = _AsyncSystemContextAPI(transport, "slack")
        self.github = _AsyncSystemContextAPI(transport, "github")
        self.datadog = _AsyncSystemContextAPI(transport, "datadog")
        self.sentry = _AsyncSystemContextAPI(transport, "sentry")
        self.aws_cloudtrail = _AsyncSystemContextAPI(transport, "aws_cloudtrail")
        self.terraform = _AsyncSystemContextAPI(transport, "terraform")
        self.kubernetes = _AsyncSystemContextAPI(transport, "kubernetes")
        self.argocd = _AsyncSystemContextAPI(transport, "argocd")
        self.gitlab = _AsyncSystemContextAPI(transport, "gitlab")
        self.jenkins = _AsyncSystemContextAPI(transport, "jenkins")
        self.azure = _AsyncSystemContextAPI(transport, "azure")
        self.prometheus = _AsyncSystemContextAPI(transport, "prometheus")
        self.grafana = _AsyncSystemContextAPI(transport, "grafana")
        self.openshift = _AsyncSystemContextAPI(transport, "openshift")

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

    async def list_connections(self, *, org_id: object = None) -> JSONDict:
        return await self._transport.request(method="GET", path="/integrations/connections", params=_params(org_id=org_id))

    async def connection(self, provider: str, *, org_id: object = None) -> SystemConnectionResponse:
        return await _AsyncSystemContextAPI(self._transport, provider).connection(org_id=org_id)

    async def test_connection(self, provider: str, config: JSONDict, *, org_id: object = None) -> SystemConnectionResponse:
        return await _AsyncSystemContextAPI(self._transport, provider).test(config, org_id=org_id)

    async def save_connection(
        self,
        provider: str,
        config: JSONDict,
        *,
        org_id: object = None,
        display_name: Optional[str] = None,
    ) -> SystemConnectionResponse:
        return await _AsyncSystemContextAPI(self._transport, provider).save(config, org_id=org_id, display_name=display_name)

    async def delete_connection(self, provider: str, *, org_id: object = None) -> JSONDict:
        return await _AsyncSystemContextAPI(self._transport, provider).delete(org_id=org_id)

    async def poll(self, provider: str, *, org_id: object = None) -> JSONDict:
        return await _AsyncSystemContextAPI(self._transport, provider).poll(org_id=org_id)

    async def poll_schedule(self, provider: str, *, org_id: object = None) -> SystemPollScheduleResponse:
        return await _AsyncSystemContextAPI(self._transport, provider).schedule(org_id=org_id)

    async def update_poll_schedule(
        self,
        provider: str,
        *,
        enabled: bool = True,
        interval_seconds: int = 300,
        max_backoff_seconds: int = 3600,
        org_id: object = None,
    ) -> SystemPollScheduleResponse:
        return await _AsyncSystemContextAPI(self._transport, provider).update_schedule(
            enabled=enabled,
            interval_seconds=interval_seconds,
            max_backoff_seconds=max_backoff_seconds,
            org_id=org_id,
        )

    async def poll_history(self, provider: str, *, limit: int = 50, org_id: object = None) -> SystemPollHistoryResponse:
        return await _AsyncSystemContextAPI(self._transport, provider).history(limit=limit, org_id=org_id)

    async def poll_status(self, *, org_id: object = None) -> SystemPollStatusResponse:
        return await self._transport.request(method="GET", path="/integrations/poll/status", params=_params(org_id=org_id))

    async def poll_metrics(self, *, org_id: object = None) -> SystemPollMetricsResponse:
        return await self._transport.request(method="GET", path="/integrations/poll/metrics", params=_params(org_id=org_id))

    async def run_due_polls(self, *, org_id: object = None) -> JSONDict:
        return await self._transport.request(method="POST", path="/integrations/poll/run-due", params=_params(org_id=org_id))

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

    def __getattr__(self, name: str) -> Any:
        if name in PROVIDER_ALIASES:
            return _AsyncSystemContextAPI(self._transport, name)
        raise AttributeError(name)
