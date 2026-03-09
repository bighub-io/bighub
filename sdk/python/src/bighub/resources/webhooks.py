from __future__ import annotations

from typing import Dict, Optional, overload

from ..models import WebhookCreateModel, WebhookUpdateModel, to_payload
from ..protocols import AsyncTransportProtocol, SyncTransportProtocol
from ..types import JSONDict, WebhookCreateRequest, WebhookInfo, WebhookUpdateRequest


class WebhooksAPI:
    """Sync API for webhook lifecycle and delivery operations."""

    def __init__(self, transport: SyncTransportProtocol) -> None:
        self._transport = transport

    @overload
    def create(self, payload: WebhookCreateRequest) -> JSONDict:
        ...

    @overload
    def create(self, payload: WebhookCreateModel) -> JSONDict:
        ...

    def create(self, payload: WebhookCreateRequest | WebhookCreateModel) -> JSONDict:
        return self._transport.request(method="POST", path="/webhooks", json_body=to_payload(payload))

    def list(self, *, include_inactive: bool = False) -> JSONDict:
        return self._transport.request(
            method="GET",
            path="/webhooks",
            params={"include_inactive": include_inactive},
        )

    def get(self, webhook_id: str) -> WebhookInfo:
        return self._transport.request(method="GET", path=f"/webhooks/{webhook_id}")

    @overload
    def update(self, webhook_id: str, payload: WebhookUpdateRequest) -> JSONDict:
        ...

    @overload
    def update(self, webhook_id: str, payload: WebhookUpdateModel) -> JSONDict:
        ...

    @overload
    def update(self, webhook_id: str, payload: JSONDict) -> JSONDict:
        ...

    def update(self, webhook_id: str, payload: WebhookUpdateRequest | WebhookUpdateModel | JSONDict) -> JSONDict:
        return self._transport.request(method="PATCH", path=f"/webhooks/{webhook_id}", json_body=to_payload(payload))

    def delete(self, webhook_id: str) -> JSONDict:
        return self._transport.request(method="DELETE", path=f"/webhooks/{webhook_id}")

    def deliveries(self, webhook_id: str, *, limit: Optional[int] = None) -> JSONDict:
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        return self._transport.request(method="GET", path=f"/webhooks/{webhook_id}/deliveries", params=params)

    def test(self, webhook_id: str, *, event_type: str = "signal.new") -> JSONDict:
        return self._transport.request(
            method="POST",
            path=f"/webhooks/{webhook_id}/test",
            json_body={"event_type": event_type},
        )

    def list_events(self) -> JSONDict:
        return self._transport.request(method="GET", path="/webhooks/events/list")

    def verify_signature(
        self,
        *,
        payload: str,
        signature: str,
        secret: str,
        timestamp: int,
    ) -> JSONDict:
        return self._transport.request(
            method="POST",
            path="/webhooks/verify-signature",
            json_body={
                "payload": payload,
                "signature": signature,
                "secret": secret,
                "timestamp": timestamp,
            },
        )

    def replay_failed_delivery(self, webhook_id: str, delivery_id: int) -> JSONDict:
        return self._transport.request(
            method="POST",
            path=f"/webhooks/{webhook_id}/deliveries/{delivery_id}/replay",
        )


class AsyncWebhooksAPI:
    """Async API for webhook lifecycle and delivery operations."""

    def __init__(self, transport: AsyncTransportProtocol) -> None:
        self._transport = transport

    @overload
    async def create(self, payload: WebhookCreateRequest) -> JSONDict:
        ...

    @overload
    async def create(self, payload: WebhookCreateModel) -> JSONDict:
        ...

    async def create(self, payload: WebhookCreateRequest | WebhookCreateModel) -> JSONDict:
        return await self._transport.request(method="POST", path="/webhooks", json_body=to_payload(payload))

    async def list(self, *, include_inactive: bool = False) -> JSONDict:
        return await self._transport.request(
            method="GET",
            path="/webhooks",
            params={"include_inactive": include_inactive},
        )

    async def get(self, webhook_id: str) -> WebhookInfo:
        return await self._transport.request(method="GET", path=f"/webhooks/{webhook_id}")

    @overload
    async def update(self, webhook_id: str, payload: WebhookUpdateRequest) -> JSONDict:
        ...

    @overload
    async def update(self, webhook_id: str, payload: WebhookUpdateModel) -> JSONDict:
        ...

    @overload
    async def update(self, webhook_id: str, payload: JSONDict) -> JSONDict:
        ...

    async def update(self, webhook_id: str, payload: WebhookUpdateRequest | WebhookUpdateModel | JSONDict) -> JSONDict:
        return await self._transport.request(method="PATCH", path=f"/webhooks/{webhook_id}", json_body=to_payload(payload))

    async def delete(self, webhook_id: str) -> JSONDict:
        return await self._transport.request(method="DELETE", path=f"/webhooks/{webhook_id}")

    async def deliveries(self, webhook_id: str, *, limit: Optional[int] = None) -> JSONDict:
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        return await self._transport.request(method="GET", path=f"/webhooks/{webhook_id}/deliveries", params=params)

    async def test(self, webhook_id: str, *, event_type: str = "signal.new") -> JSONDict:
        return await self._transport.request(
            method="POST",
            path=f"/webhooks/{webhook_id}/test",
            json_body={"event_type": event_type},
        )

    async def list_events(self) -> JSONDict:
        return await self._transport.request(method="GET", path="/webhooks/events/list")

    async def verify_signature(
        self,
        *,
        payload: str,
        signature: str,
        secret: str,
        timestamp: int,
    ) -> JSONDict:
        return await self._transport.request(
            method="POST",
            path="/webhooks/verify-signature",
            json_body={
                "payload": payload,
                "signature": signature,
                "secret": secret,
                "timestamp": timestamp,
            },
        )

    async def replay_failed_delivery(self, webhook_id: str, delivery_id: int) -> JSONDict:
        return await self._transport.request(
            method="POST",
            path=f"/webhooks/{webhook_id}/deliveries/{delivery_id}/replay",
        )
