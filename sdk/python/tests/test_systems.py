from __future__ import annotations

import json

import httpx
import pytest

from bighub import BighubClient


def test_systems_provider_aliases_and_display_name() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/integrations/kubernetes/connection" and request.method == "PUT":
            payload = json.loads(request.content.decode("utf-8"))
            assert payload == {"kubeconfig": "redacted", "display_name": "Production Kubernetes"}
            return httpx.Response(200, json={"provider": "kubernetes", "configured": True})
        if request.url.path == "/integrations/argocd/poll/history" and request.method == "GET":
            assert request.url.params.get("limit") == "25"
            return httpx.Response(200, json={"provider": "argocd", "history": []})
        raise AssertionError(f"Unexpected {request.method} {request.url.path}")

    client = BighubClient(api_key="bhk_test")
    client._transport._client = httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0)

    saved = client.systems.save_connection(
        "k8s",
        {"kubeconfig": "redacted"},
        display_name="Production Kubernetes",
    )
    history = client.systems.poll_history("argo-cd", limit=25)

    assert saved["provider"] == "kubernetes"
    assert history["provider"] == "argocd"
    client.close()


def test_systems_reject_unknown_provider_before_http_call() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return httpx.Response(500, json={"detail": "should not be called"})

    client = BighubClient(api_key="bhk_test")
    client._transport._client = httpx.Client(transport=httpx.MockTransport(handler), timeout=5.0)

    with pytest.raises(ValueError, match="Unsupported BIGHUB system provider"):
        client.systems.connection("unknown-ci")

    assert calls["count"] == 0
    client.close()
