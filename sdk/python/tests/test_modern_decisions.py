from __future__ import annotations

import ast
import json
from pathlib import Path

import httpx
import pytest

from bighub import AsyncBighubClient, AsyncDecision, Bighub, BighubClient, Decision, DecisionBrief, DecisionPacket, ModelSelection


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "canonical_better_decision_response.json"


def _canonical_payload() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _decision_payload() -> dict:
    return {
        "request_id": "req_123",
        "recommendation": "proceed_with_caution",
        "recommendation_confidence": "high",
        "risk_score": 0.42,
        "mode": "LIMITED",
        "selected_model": "gpt-5.5",
        "selected_decision_path": "gpt-5.5 + packet",
        "model_selection_reason": "Production Okta access requires packet reasoning.",
        "decision_packet": {
            "intent": "better_decision",
            "action_type": "access_change",
            "system": "okta",
            "environment": "production",
            "context": {"system": "okta", "environment": "production"},
            "candidate_actions": ["Grant scoped Okta admin access for 48h"],
            "risk_factors": ["privileged access"],
            "verification_plan": ["Confirm entitlement after provisioning"],
            "obligations": [{"type": "revoke_access", "due_in": "48h"}],
            "learning_hooks": ["capture_review_outcome"],
        },
        "decision_intelligence": {
            "rationale": "Use a narrower group and time-boxed access.",
            "projected_regret": 0.18,
            "alternatives": [
                {"action": "Grant scoped Okta admin access for 48h", "rationale": "Least privilege"}
            ],
            "precedents": {"total_precedents": 7},
        },
    }


def test_sdk_maps_canonical_backend_better_decision_contract() -> None:
    payload = _canonical_payload()
    decision = Decision.from_backend_response(payload)

    assert decision.request_id == "VAL_1010"
    assert decision.proposed_action == payload["proposed_action"]
    assert decision.better_action == payload["better_action"]
    assert decision.mode == "review"
    assert decision.risk == 0.68
    assert decision.confidence == 0.84
    assert decision.expected_regret == 0.31
    assert decision.can_run is False
    assert decision.needs_review is True
    assert decision.should_not_run is False
    assert decision.selected_model is None
    assert decision.model_selection.selected_model is None
    assert decision.model_selection.review_required is True
    assert decision.packet.system == "okta"
    assert decision.packet.packet_sha256 == payload["decision_packet"]["packet_sha256"]
    assert decision.packet.packet_sha256_is_local is False
    assert decision.brain.reasoning_summary == payload["decision_brain"]["reasoning_summary"]
    assert decision.brain.confidence == 0.84
    assert decision.brain.world_state_used is True
    assert decision.reason == payload["reason"]

    brief = decision.brief()
    assert isinstance(brief, DecisionBrief)
    assert brief.request_id == "VAL_1010"
    assert brief.recommended_action == payload["better_action"]
    assert brief.needs_review is True
    assert brief.system == "okta"
    assert brief.world_state_used is True
    assert brief.to_dict()["recommendation"] == payload["decision_brain"]["recommendation"]


def test_bighub_decide_returns_decision_object() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/actions/evaluate"
        payload = json.loads(request.content.decode("utf-8"))
        assert payload["action"].startswith("Grant temporary Okta")
        assert payload["context"]["objective"] == "better_decision"
        assert payload["context"]["model_selection"] == "auto"
        return httpx.Response(200, json=_decision_payload())

    bighub = Bighub(api_key="bhk_test")
    bighub._transport._client = httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0)

    decision = bighub.decide(
        action="Grant temporary Okta admin access to users 1-9 for 48h",
        context={"system": "okta", "environment": "production"},
        model_selection="auto",
    )

    assert isinstance(decision, Decision)
    assert decision.request_id == "req_123"
    assert decision.better_action == "Grant scoped Okta admin access for 48h"
    assert decision.selected_model == "gpt-5.5"
    assert decision.decision_path == "gpt-5.5 + packet"
    assert decision.mode == "constrained"
    assert decision.can_run is True
    assert decision.needs_review is False
    assert decision.risk == 0.42
    assert decision.confidence is None
    assert decision.packet.system == "okta"
    assert decision.packet.packet_sha256_is_local is True
    assert decision.brain.precedent_count == 7
    bighub.close()


def test_client_decisions_evaluate_and_legacy_actions_evaluate_both_work() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if len(calls) in {1, 2}:
            return httpx.Response(200, json=_decision_payload())
        return httpx.Response(200, json={"allowed": True, "result": "allowed"})

    client = BighubClient(api_key="bhk_test")
    client._transport._client = httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0)

    decision = client.decisions.evaluate(action="Rotate database credentials", context={"system": "database"})
    raw = client.decisions.evaluate(action="Rotate database credentials", context={"system": "database"}, raw=True)
    legacy = client.actions.evaluate(action="Rotate database credentials", context={"system": "database"})

    assert decision.better_action == "Grant scoped Okta admin access for 48h"
    assert raw["request_id"] == "req_123"
    assert legacy["allowed"] is True
    assert calls == ["/actions/evaluate", "/actions/evaluate", "/actions/evaluate"]
    client.close()


def test_decision_maps_partial_payload_without_inventing_model_fields() -> None:
    raw = {
        "request_id": "req_partial",
        "allowed": True,
        "result": "allowed",
        "recommendation": "proceed",
        "risk_score": 0.08,
    }

    decision = Decision.from_backend_response(raw, proposed_action="Post Slack incident summary")

    assert decision.request_id == "req_partial"
    assert decision.proposed_action == "Post Slack incident summary"
    assert decision.better_action is None
    assert decision.selected_model is None
    assert decision.model_selection_reason is None
    assert decision.decision_path is None
    assert decision.mode == "autonomous"
    assert decision.can_run is True
    assert decision.packet.packet_sha256 is None
    assert decision.brain.confidence is None
    assert ModelSelection.from_backend_response(raw).selected_model is None


def test_decision_packet_maps_backend_packet_shape() -> None:
    packet = DecisionPacket.from_payload(
        {
            "version": 1,
            "signal": {"recommendation": "review_recommended", "risk_score": 0.67},
            "context": {"projected_regret": {"score": 0.44}},
            "alternatives": [{"action": "Reduce scope to one user", "estimated_risk": 0.21}],
        }
    )

    assert packet.raw["version"] == 1
    assert packet.intent is None
    assert packet.candidate_actions == []
    assert packet.packet_sha256
    assert packet.packet_sha256_is_local is True


def test_decision_packet_hash_uses_canonical_json() -> None:
    packet = DecisionPacket.build(
        action="Grant access",
        context={"system": "okta", "environment": "prod"},
        system="okta",
        environment="prod",
    )

    assert packet.packet_sha256 == "c4c66e9f0d21a1071aa45bb408b6adbc79546b97e8f8332099b5dd86643e5b6e"


def test_decision_request_review_and_report_outcome_call_expected_apis() -> None:
    seen: list[tuple[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append((request.method, request.url.path))
        if request.url.path == "/actions/evaluate":
            payload = _decision_payload()
            payload["recommendation"] = "review_recommended"
            payload["human_review"] = True
            return httpx.Response(200, json=payload)
        if request.url.path == "/approvals":
            return httpx.Response(200, json=[{"request_id": "req_123", "status": "pending"}])
        if request.url.path == "/outcomes/report":
            body = json.loads(request.content.decode("utf-8"))
            assert body["request_id"] == "req_123"
            assert body["status"] == "completed"
            assert body["human_final_action"] == "Grant scoped Okta admin access for 48h"
            assert body["details"]["deployment_id"] == "dep_123"
            return httpx.Response(200, json={"ok": True})
        raise AssertionError(f"Unexpected {request.method} {request.url.path}")

    client = BighubClient(api_key="bhk_test")
    client._transport._client = httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0)

    decision = client.decide(action="Deploy payment-service", context={"system": "github"})
    review = decision.request_review(reason="prod deploy")
    outcome = decision.report_outcome(status="completed", evidence={"deployment_id": "dep_123"})

    assert decision.needs_review is True
    assert review["status"] == "pending"
    assert outcome["ok"] is True
    assert seen == [("POST", "/actions/evaluate"), ("GET", "/approvals"), ("POST", "/outcomes/report")]
    client.close()


def test_packets_brain_and_systems_surfaces() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/actions/evaluate":
            return httpx.Response(200, json=_decision_payload())
        if request.url.path == "/world-state/operational":
            return httpx.Response(200, json={"risk_posture": "caution", "subsystems": []})
        if request.url.path == "/integrations/okta/connection":
            return httpx.Response(200, json={"configured": True, "provider": "okta"})
        raise AssertionError(f"Unexpected {request.method} {request.url.path}")

    client = BighubClient(api_key="bhk_test")
    client._transport._client = httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0)

    packet = client.build_packet(
        action="Export sensitive data",
        context={"system": "database", "environment": "production"},
    )
    brain = client.run_brain(packet=packet)
    world = client.systems.world_state()
    okta = client.systems.okta.context()

    assert packet.packet_sha256
    assert brain.recommendation == "proceed_with_caution"
    assert world["risk_posture"] == "caution"
    assert okta["configured"] is True
    client.close()


@pytest.mark.asyncio
async def test_async_client_exposes_decide() -> None:
    seen: list[tuple[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append((request.method, request.url.path))
        if request.url.path == "/outcomes/report":
            return httpx.Response(200, json={"ok": True})
        if request.url.path == "/approvals":
            return httpx.Response(200, json=[{"request_id": "req_123", "status": "pending"}])
        assert request.url.path == "/actions/evaluate"
        return httpx.Response(200, json=_decision_payload())

    client = AsyncBighubClient(api_key="bhk_test")
    client._transport._client = httpx.AsyncClient(transport=httpx.MockTransport(handler), timeout=5.0)

    decision = await client.decide(action="Post incident summary", context={"system": "slack"})

    assert isinstance(decision, AsyncDecision)
    assert decision.better_action == "Grant scoped Okta admin access for 48h"
    assert decision.selected_model == "gpt-5.5"
    outcome = await decision.report_outcome(status="completed", evidence={"message_ts": "1.2"})
    review = await decision.request_review(reason="manual smoke")
    assert outcome["ok"] is True
    assert review["status"] == "pending"
    assert seen == [("POST", "/actions/evaluate"), ("POST", "/outcomes/report"), ("GET", "/approvals")]
    await client.close()


def test_readme_quickstart_is_syntax_valid() -> None:
    readme = Path(__file__).resolve().parents[1] / "README.md"
    text = readme.read_text(encoding="utf-8")
    marker = "```python"
    start = text.index(marker) + len(marker)
    end = text.index("```", start)
    ast.parse(text[start:end].strip())
