from __future__ import annotations

import json
import httpx
import pytest

from bighub import AsyncBighubClient


@pytest.mark.asyncio
async def test_async_client_submit() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/actions/evaluate"
        return httpx.Response(200, json={"allowed": True, "risk_score": 0.1})

    client = AsyncBighubClient(api_key="bhk_test")
    client._transport._client = httpx.AsyncClient(transport=httpx.MockTransport(handler), timeout=5.0)

    result = await client.actions.submit(action="update_price", value=120.0, domain="financial_actions")
    assert result["allowed"] is True
    await client.close()


@pytest.mark.asyncio
async def test_async_constraints_validate_dry_run_and_kill_switch() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/rules/validate/dry-run":
            return httpx.Response(200, json={"allowed": False, "dry_run": True})
        if request.url.path == "/kill-switch/status":
            return httpx.Response(200, json={"is_active": True, "active_switches": [{"id": "ksw_1"}]})
        raise AssertionError(f"Unexpected path: {request.url.path}")

    client = AsyncBighubClient(api_key="bhk_test")
    client._transport._client = httpx.AsyncClient(transport=httpx.MockTransport(handler), timeout=5.0)

    validate_result = await client.constraints.validate_dry_run({"action": "reorder_stock", "actor": "AI_AGENT"})
    kill_switch_result = await client.kill_switch.status()

    assert validate_result["dry_run"] is True
    assert kill_switch_result["is_active"] is True
    await client.close()


@pytest.mark.asyncio
async def test_async_webhooks_management_paths() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/webhooks" and request.method == "POST":
            return httpx.Response(200, json={"webhook_id": "wh_async"})
        if request.url.path == "/webhooks/wh_async/deliveries/1/replay" and request.method == "POST":
            return httpx.Response(200, json={"replayed": True})
        if request.url.path == "/webhooks/verify-signature" and request.method == "POST":
            return httpx.Response(200, json={"valid": True})
        raise AssertionError(f"Unexpected {request.method} {request.url.path}")

    client = AsyncBighubClient(api_key="bhk_test")
    client._transport._client = httpx.AsyncClient(transport=httpx.MockTransport(handler), timeout=5.0)

    created = await client.webhooks.create({"url": "https://example.com/hook"})
    replayed = await client.webhooks.replay_failed_delivery("wh_async", 1)
    verified = await client.webhooks.verify_signature(
        payload="{}",
        signature="v1=abc",
        secret="sec",
        timestamp=1700000000,
    )

    assert created["webhook_id"] == "wh_async"
    assert replayed["replayed"] is True
    assert verified["valid"] is True
    await client.close()


@pytest.mark.asyncio
async def test_async_api_keys_management_paths() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api-keys" and request.method == "POST":
            return httpx.Response(200, json={"key_id": "key_async"})
        if request.url.path == "/api-keys/key_async/rotate" and request.method == "POST":
            return httpx.Response(200, json={"new_key_id": "key_async_2"})
        if request.url.path == "/api-keys/scopes" and request.method == "GET":
            return httpx.Response(200, json={"scopes": ["rules:read"]})
        raise AssertionError(f"Unexpected {request.method} {request.url.path}")

    client = AsyncBighubClient(api_key="bhk_test")
    client._transport._client = httpx.AsyncClient(transport=httpx.MockTransport(handler), timeout=5.0)

    created = await client.api_keys.create({"label": "async"})
    rotated = await client.api_keys.rotate("key_async")
    scopes = await client.api_keys.scopes()

    assert created["key_id"] == "key_async"
    assert rotated["new_key_id"] == "key_async_2"
    assert "rules:read" in scopes["scopes"]
    await client.close()


@pytest.mark.asyncio
async def test_async_auth_events_approvals_paths() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/auth/login" and request.method == "POST":
            return httpx.Response(200, json={"access_token": "a_async", "refresh_token": "r_async", "user_id": 2, "role": "user"})
        if request.url.path == "/events/stats" and request.method == "GET":
            return httpx.Response(200, json={"today": {"blocked": 1}, "total": {"blocked": 10}})
        if request.url.path == "/approvals/apr_async/resolve" and request.method == "POST":
            return httpx.Response(200, json={"request_id": "apr_async", "status": "denied"})
        raise AssertionError(f"Unexpected {request.method} {request.url.path}")

    client = AsyncBighubClient(api_key="bhk_test")
    client._transport._client = httpx.AsyncClient(transport=httpx.MockTransport(handler), timeout=5.0)

    login = await client.auth.login({"email": "x@y.com", "password": "pass1234"})
    stats = await client.events.stats()
    resolved = await client.approvals.resolve("apr_async", resolution="denied", comment="unsafe")

    assert login["access_token"] == "a_async"
    assert stats["today"]["blocked"] == 1
    assert resolved["status"] == "denied"
    await client.close()


@pytest.mark.asyncio
async def test_async_contract_aliases_for_actions_retrieval_and_ingest_reconcile() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/actions/evaluate" and request.method == "POST":
            payload = json.loads(request.content.decode("utf-8"))
            assert payload["context"] == {"order_id": "ord_async"}
            assert "metadata" not in payload
            return httpx.Response(200, json={"allowed": True})
        if request.url.path == "/retrieval/query/explained" and request.method == "POST":
            payload = json.loads(request.content.decode("utf-8"))
            assert payload["strategy"] == "balanced"
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/ingest/reconcile" and request.method == "POST":
            payload = json.loads(request.content.decode("utf-8"))
            assert payload["key_name"] == "request_id"
            assert payload["key_value"] == "req_async"
            assert payload["outcome"]["event_type"] == "OUTCOME_OBSERVED"
            return httpx.Response(200, json={"status": "reconciled"})
        raise AssertionError(f"Unexpected {request.method} {request.url.path}")

    client = AsyncBighubClient(api_key="bhk_test")
    client._transport._client = httpx.AsyncClient(transport=httpx.MockTransport(handler), timeout=5.0)

    submit = await client.actions.submit(action="refund_full", metadata={"order_id": "ord_async"})
    retrieval = await client.retrieval.query_explained(
        domain="customer_transactions",
        action="refund_full",
        strategy="balanced",
    )
    reconcile = await client.ingest.reconcile(
        request_id="req_async",
        outcome={"event_type": "OUTCOME_OBSERVED", "outcome": {"status": "SUCCESS"}},
    )

    assert submit["allowed"] is True
    assert retrieval["status"] == "ok"
    assert reconcile["status"] == "reconciled"
    await client.close()
