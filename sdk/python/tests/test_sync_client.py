from __future__ import annotations

import json
import httpx

from bighub import BighubClient


def test_sync_client_sends_api_key_header() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("x-api-key") == "bhk_test"
        return httpx.Response(200, json={"ok": True})

    client = BighubClient(api_key="bhk_test")
    client._transport._client = httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0)

    response = client.actions.status()
    assert response["ok"] is True
    client.close()


def test_sync_client_retries_transient_500() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(500, json={"detail": "temporary"})
        return httpx.Response(200, json={"ok": True})

    client = BighubClient(api_key="bhk_test", max_retries=1)
    client._transport._client = httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0)

    response = client.actions.status()
    assert response["ok"] is True
    assert calls["n"] == 2
    client.close()


def test_sync_rules_validate_and_domains() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/rules/validate":
            return httpx.Response(200, json={"allowed": True, "result": "allowed"})
        if request.url.path == "/rules/domains":
            return httpx.Response(200, json=[{"id": "financial_actions"}])
        if request.url.path == "/rules/rule_1/apply_patch" and request.method == "POST":
            payload = json.loads(request.content.decode("utf-8"))
            assert payload["patch"][0]["op"] == "replace"
            assert payload["patch"][0]["path"] == "/max_value"
            assert payload["if_match_version"] == 11
            assert request.headers.get("if-match") == 'W/"rule:rule_1:v11"'
            return httpx.Response(
                200,
                json={
                    "rule_id": "rule_1",
                    "preview": True,
                    "applied": False,
                    "patch_valid": True,
                    "changed_paths": ["/max_value"],
                    "diff_summary": "1 field changed: max_value",
                    "changed_fields": [{"field": "max_value", "before": 1000.0, "after": 850.0}],
                    "patch_hash": "sha256:test",
                    "applied_by": "user:test@bighub.io",
                    "before": {"max_value": 1000.0},
                    "after": {"max_value": 850.0},
                },
            )
        raise AssertionError(f"Unexpected path: {request.url.path}")

    client = BighubClient(api_key="bhk_test")
    client._transport._client = httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0)

    validate_result = client.rules.validate({"action": "update_price", "actor": "AI_AGENT"})
    domains_result = client.rules.domains()
    patch_preview = client.rules.apply_patch(
        "rule_1",
        patch={"format": "json_patch", "ops": [{"op": "replace", "path": "/max_value", "value": 850.0}]},
        preview=True,
        reason="memory recommendation",
        if_match_version=11,
        if_match='W/"rule:rule_1:v11"',
    )

    assert validate_result["allowed"] is True
    assert domains_result[0]["id"] == "financial_actions"
    assert patch_preview["patch_valid"] is True
    assert patch_preview["changed_fields"][0]["field"] == "max_value"
    assert patch_preview["changed_paths"][0] == "/max_value"
    client.close()


def test_sync_kill_switch_paths() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/kill-switch/status":
            return httpx.Response(200, json={"is_active": False, "active_switches": []})
        if request.url.path == "/kill-switch/activate":
            return httpx.Response(200, json={"switch_id": "ksw_123"})
        if request.url.path == "/kill-switch/deactivate/ksw_123":
            return httpx.Response(200, json={"success": True})
        raise AssertionError(f"Unexpected path: {request.url.path}")

    client = BighubClient(api_key="bhk_test")
    client._transport._client = httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0)

    status_result = client.kill_switch.status()
    activate_result = client.kill_switch.activate({"reason": "maintenance"})
    deactivate_result = client.kill_switch.deactivate("ksw_123", {"reason": "resume ops"})

    assert status_result["is_active"] is False
    assert activate_result["switch_id"] == "ksw_123"
    assert deactivate_result["success"] is True
    client.close()


def test_sync_webhooks_management_paths() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/webhooks" and request.method == "POST":
            return httpx.Response(200, json={"webhook_id": "wh_1"})
        if request.url.path == "/webhooks" and request.method == "GET":
            assert request.url.params.get("include_inactive") == "true"
            return httpx.Response(200, json=[{"webhook_id": "wh_1"}])
        if request.url.path == "/webhooks/wh_1" and request.method == "GET":
            return httpx.Response(200, json={"webhook_id": "wh_1", "label": "prod"})
        if request.url.path == "/webhooks/wh_1" and request.method == "PATCH":
            return httpx.Response(200, json={"status": "updated"})
        if request.url.path == "/webhooks/wh_1" and request.method == "DELETE":
            return httpx.Response(200, json={"status": "deleted"})
        if request.url.path == "/webhooks/wh_1/deliveries" and request.method == "GET":
            assert request.url.params.get("limit") == "10"
            return httpx.Response(200, json=[{"delivery_id": 123}])
        if request.url.path == "/webhooks/wh_1/test" and request.method == "POST":
            return httpx.Response(200, json={"status": "delivered"})
        if request.url.path == "/webhooks/verify-signature" and request.method == "POST":
            return httpx.Response(200, json={"valid": True})
        if request.url.path == "/webhooks/events/list" and request.method == "GET":
            return httpx.Response(200, json={"events": ["signal.new"]})
        if request.url.path == "/webhooks/wh_1/deliveries/123/replay" and request.method == "POST":
            return httpx.Response(200, json={"replayed": True})
        raise AssertionError(f"Unexpected {request.method} {request.url.path}")

    client = BighubClient(api_key="bhk_test")
    client._transport._client = httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0)

    created = client.webhooks.create({"url": "https://example.com/hook"})
    listed = client.webhooks.list(include_inactive=True)
    got = client.webhooks.get("wh_1")
    updated = client.webhooks.update("wh_1", {"label": "new-label"})
    deliveries = client.webhooks.deliveries("wh_1", limit=10)
    tested = client.webhooks.test("wh_1", event_type="signal.new")
    verified = client.webhooks.verify_signature(
        payload="{}",
        signature="v1=abc",
        secret="sec",
        timestamp=1700000000,
    )
    events = client.webhooks.list_events()
    replayed = client.webhooks.replay_failed_delivery("wh_1", 123)
    deleted = client.webhooks.delete("wh_1")

    assert created["webhook_id"] == "wh_1"
    assert listed[0]["webhook_id"] == "wh_1"
    assert got["webhook_id"] == "wh_1"
    assert updated["status"] == "updated"
    assert deliveries[0]["delivery_id"] == 123
    assert tested["status"] == "delivered"
    assert verified["valid"] is True
    assert events["events"][0] == "signal.new"
    assert replayed["replayed"] is True
    assert deleted["status"] == "deleted"
    client.close()


def test_sync_api_keys_management_paths() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api-keys" and request.method == "POST":
            return httpx.Response(200, json={"key_id": "key_1", "key": "bhk_secret"})
        if request.url.path == "/api-keys" and request.method == "GET":
            assert request.url.params.get("include_revoked") == "true"
            return httpx.Response(200, json={"count": 1, "keys": [{"key_id": "key_1"}]})
        if request.url.path == "/api-keys/key_1" and request.method == "DELETE":
            return httpx.Response(200, json={"status": "revoked"})
        if request.url.path == "/api-keys/key_1/rotate" and request.method == "POST":
            return httpx.Response(200, json={"new_key_id": "key_2"})
        if request.url.path == "/api-keys/validate" and request.method == "GET":
            assert request.url.params.get("api_key") == "bhk_secret"
            return httpx.Response(200, json={"valid": True})
        if request.url.path == "/api-keys/scopes" and request.method == "GET":
            return httpx.Response(200, json={"scopes": ["actions:validate"]})
        raise AssertionError(f"Unexpected {request.method} {request.url.path}")

    client = BighubClient(api_key="bhk_test")
    client._transport._client = httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0)

    created = client.api_keys.create({"label": "prod"})
    listed = client.api_keys.list(include_revoked=True)
    deleted = client.api_keys.delete("key_1", reason="rotated")
    rotated = client.api_keys.rotate("key_1")
    validated = client.api_keys.validate("bhk_secret")
    scopes = client.api_keys.scopes()

    assert created["key_id"] == "key_1"
    assert listed["count"] == 1
    assert deleted["status"] == "revoked"
    assert rotated["new_key_id"] == "key_2"
    assert validated["valid"] is True
    assert "actions:validate" in scopes["scopes"]
    client.close()


def test_sync_actions_future_memory_paths() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/actions/memory/ingest" and request.method == "POST":
            return httpx.Response(200, json={"accepted": 1, "total_stored": 1, "source": "openai_adapter"})
        if request.url.path == "/actions/memory/context" and request.method == "GET":
            assert request.url.params.get("window_hours") == "24"
            assert request.url.params.get("tool") == "refund_payment"
            return httpx.Response(
                200,
                json={
                    "org_id": 1,
                    "window_hours": 24,
                    "filters": {"tool": "refund_payment"},
                    "total_events": 10,
                    "blocked_rate": 0.2,
                    "approval_rate": 0.1,
                    "tool_error_rate": 0.0,
                    "avg_risk_score": 0.31,
                    "top_tools": [{"tool": "refund_payment", "count": 10}],
                    "top_block_reasons": [{"blocked_by": "max_value", "count": 2}],
                    "recent_events": [],
                },
            )
        if request.url.path == "/actions/memory/refresh-aggregates" and request.method == "POST":
            assert request.url.params.get("concurrent") == "true"
            return httpx.Response(200, json={"refreshed": True, "mode": "concurrent"})
        if request.url.path == "/actions/memory/recommendations" and request.method == "POST":
            body = request.content.decode("utf-8")
            assert "\"window_hours\"" in body
            return httpx.Response(
                200,
                json={
                    "org_id": 1,
                    "plan": "pro",
                    "window_hours": 24,
                    "generated_at": "2026-02-27T00:00:00Z",
                    "filters": {"domain": "customer_transactions", "tool": "refund_payment", "actor": "AI_AGENT_001"},
                    "summary": {"total_events": 10, "blocked_rate": 0.2},
                    "recommendations": [
                        {
                            "recommendation_id": "rec_1",
                            "type": "policy_tuning_max_value",
                            "tool": "refund_payment",
                            "scope": {"domain": "customer_transactions", "tool": "refund_payment", "actor": "AI_AGENT_001"},
                            "time_window_hours": 24,
                            "requires_human_review": True,
                            "is_safe_patch": True,
                            "confidence": 0.82,
                        }
                    ],
                },
            )
        raise AssertionError(f"Unexpected {request.method} {request.url.path}")

    client = BighubClient(api_key="bhk_test")
    client._transport._client = httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0)

    ingested = client.actions.ingest_memory(
        source="openai_adapter",
        events=[
            {
                "tool": "refund_payment",
                "status": "executed",
                "decision": {"allowed": True, "result": "allowed"},
                "arguments": {"order_id": "ord_1", "amount": 120.0},
            }
        ],
    )
    context = client.actions.memory_context(window_hours=24, tool="refund_payment")
    refreshed = client.actions.refresh_memory_aggregates(concurrent=True)
    recommendations = client.actions.memory_recommendations(window_hours=24, tool="refund_payment")
    scoped_recommendations = client.actions.memory_recommendations(
        window_hours=24,
        scope={"domain": "customer_transactions", "tool": "refund_payment", "actor": "AI_AGENT_001"},
    )

    assert ingested["accepted"] == 1
    assert context["total_events"] == 10
    assert context["top_tools"][0]["tool"] == "refund_payment"
    assert refreshed["refreshed"] is True
    assert recommendations["plan"] == "pro"
    assert recommendations["recommendations"][0]["type"] == "policy_tuning_max_value"
    assert scoped_recommendations["recommendations"][0]["requires_human_review"] is True
    client.close()


def test_sync_auth_events_approvals_paths() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/auth/signup" and request.method == "POST":
            return httpx.Response(200, json={"access_token": "a1", "refresh_token": "r1", "user_id": 1, "role": "user"})
        if request.url.path == "/auth/login" and request.method == "POST":
            return httpx.Response(200, json={"access_token": "a2", "refresh_token": "r2", "user_id": 1, "role": "user"})
        if request.url.path == "/auth/refresh" and request.method == "POST":
            return httpx.Response(200, json={"access_token": "a3", "refresh_token": "r3", "user_id": 1, "role": "user"})
        if request.url.path == "/auth/logout" and request.method == "POST":
            return httpx.Response(200, json={"detail": "Logged out"})

        if request.url.path == "/events" and request.method == "GET":
            assert request.url.params.get("event_type") == "rule.updated"
            return httpx.Response(200, json={"events": []})
        if request.url.path == "/events/stats" and request.method == "GET":
            return httpx.Response(200, json={"today": {}, "total": {}})

        if request.url.path == "/approvals" and request.method == "GET":
            assert request.url.params.get("status") == "pending"
            return httpx.Response(200, json=[])
        if request.url.path == "/approvals/apr_1/resolve" and request.method == "POST":
            return httpx.Response(200, json={"request_id": "apr_1", "status": "approved"})

        raise AssertionError(f"Unexpected {request.method} {request.url.path}")

    client = BighubClient(api_key="bhk_test")
    client._transport._client = httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0)

    signup = client.auth.signup({"email": "a@b.com", "password": "pass1234"})
    login = client.auth.login({"email": "a@b.com", "password": "pass1234"})
    refresh = client.auth.refresh("r1")
    logout = client.auth.logout("r1")

    events = client.events.list(event_type="rule.updated")
    event_stats = client.events.stats()

    approvals = client.approvals.list(status_filter="pending")
    resolved = client.approvals.resolve("apr_1", resolution="approved", comment="looks good")

    assert signup["access_token"] == "a1"
    assert login["access_token"] == "a2"
    assert refresh["access_token"] == "a3"
    assert logout["detail"] == "Logged out"
    assert events["events"] == []
    assert "today" in event_stats
    assert approvals == []
    assert resolved["status"] == "approved"
    client.close()


def test_sync_contract_aliases_for_actions_retrieval_and_ingest_reconcile() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/actions/submit" and request.method == "POST":
            payload = json.loads(request.content.decode("utf-8"))
            assert payload["context"] == {"order_id": "ord_1"}
            assert "metadata" not in payload
            return httpx.Response(200, json={"allowed": True})
        if request.url.path == "/retrieval/query" and request.method == "POST":
            payload = json.loads(request.content.decode("utf-8"))
            assert payload["strategy"] == "balanced"
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/ingest/reconcile" and request.method == "POST":
            payload = json.loads(request.content.decode("utf-8"))
            assert payload["key_name"] == "request_id"
            assert payload["key_value"] == "req_123"
            assert payload["outcome"]["event_type"] == "OUTCOME_OBSERVED"
            return httpx.Response(200, json={"status": "reconciled"})
        raise AssertionError(f"Unexpected {request.method} {request.url.path}")

    client = BighubClient(api_key="bhk_test")
    client._transport._client = httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0)

    submit = client.actions.submit(
        action="refund_full",
        metadata={"order_id": "ord_1"},
    )
    retrieval = client.retrieval.query(
        domain="customer_transactions",
        action="refund_full",
        strategy="balanced",
    )
    reconcile = client.ingest.reconcile(
        request_id="req_123",
        outcome={"event_type": "OUTCOME_OBSERVED", "outcome": {"status": "SUCCESS"}},
    )

    assert submit["allowed"] is True
    assert retrieval["status"] == "ok"
    assert reconcile["status"] == "reconciled"
    client.close()
