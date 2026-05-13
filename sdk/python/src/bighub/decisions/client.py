from __future__ import annotations

from typing import Any, Optional

from ..protocols import AsyncTransportProtocol, SyncTransportProtocol
from ..types import JSONDict
from .types import AsyncDecision, Decision


def _payload(
    *,
    action: str,
    context: Optional[JSONDict],
    objective: str,
    model_selection: str,
    value: Optional[float],
    target: Optional[str],
    actor: str,
    domain: Optional[str],
    dry_run: bool,
) -> JSONDict:
    ctx = dict(context or {})
    ctx.setdefault("objective", objective)
    ctx.setdefault("model_selection", model_selection)
    payload: JSONDict = {"action": action, "actor": actor, "context": ctx}
    if value is not None:
        payload["value"] = value
    if target is not None:
        payload["target"] = target
    if domain is not None:
        payload["domain"] = domain
    if dry_run:
        payload["dry_run"] = True
    return payload


class DecisionsAPI:
    """Modern Better Decision API.

    This is the high-level SDK surface. It maps to the current BIGHUB action
    evaluation backend and returns a rich :class:`Decision` object instead of a
    raw allow/block style dictionary.
    """

    def __init__(self, transport: SyncTransportProtocol, *, reviews: Any = None, outcomes: Any = None) -> None:
        self._transport = transport
        self._reviews = reviews
        self._outcomes = outcomes

    def evaluate(
        self,
        *,
        action: str,
        context: Optional[JSONDict] = None,
        objective: str = "better_decision",
        model_selection: str = "auto",
        value: Optional[float] = None,
        target: Optional[str] = None,
        actor: str = "AI_AGENT",
        domain: Optional[str] = None,
        dry_run: bool = False,
        idempotency_key: Optional[str] = None,
        raw: bool = False,
    ) -> Decision | JSONDict:
        body = _payload(
            action=action,
            context=context,
            objective=objective,
            model_selection=model_selection,
            value=value,
            target=target,
            actor=actor,
            domain=domain,
            dry_run=dry_run,
        )
        response = self._transport.request(
            method="POST",
            path="/actions/evaluate",
            json_body=body,
            idempotency_key=idempotency_key,
        )
        if raw:
            return response
        return Decision.from_response(
            response,
            proposed_action=action,
            context=body.get("context"),
            requested_model_selection=model_selection,
            reviews=self._reviews,
            outcomes=self._outcomes,
        )

    decide = evaluate


class AsyncDecisionsAPI:
    """Async modern Better Decision API."""

    def __init__(self, transport: AsyncTransportProtocol, *, reviews: Any = None, outcomes: Any = None) -> None:
        self._transport = transport
        self._reviews = reviews
        self._outcomes = outcomes

    async def evaluate(
        self,
        *,
        action: str,
        context: Optional[JSONDict] = None,
        objective: str = "better_decision",
        model_selection: str = "auto",
        value: Optional[float] = None,
        target: Optional[str] = None,
        actor: str = "AI_AGENT",
        domain: Optional[str] = None,
        dry_run: bool = False,
        idempotency_key: Optional[str] = None,
        raw: bool = False,
    ) -> AsyncDecision | JSONDict:
        body = _payload(
            action=action,
            context=context,
            objective=objective,
            model_selection=model_selection,
            value=value,
            target=target,
            actor=actor,
            domain=domain,
            dry_run=dry_run,
        )
        response = await self._transport.request(
            method="POST",
            path="/actions/evaluate",
            json_body=body,
            idempotency_key=idempotency_key,
        )
        if raw:
            return response
        base = Decision.from_response(
            response,
            proposed_action=action,
            context=body.get("context"),
            requested_model_selection=model_selection,
            reviews=self._reviews,
            outcomes=self._outcomes,
        )
        return AsyncDecision(**base.__dict__)

    decide = evaluate
