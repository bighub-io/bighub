from __future__ import annotations

from typing import Optional

from ..brain.types import DecisionBrainResult
from ..packets.types import DecisionPacket
from ..protocols import AsyncTransportProtocol, SyncTransportProtocol
from ..types import JSONDict


def _body_from_packet(packet: DecisionPacket, *, action: Optional[str], actor: str) -> JSONDict:
    proposed = action or (str(packet.candidate_actions[0]) if packet.candidate_actions else "")
    context = dict(packet.context or {})
    context["decision_packet"] = packet.to_dict()
    return {
        "action": proposed,
        "actor": actor,
        "domain": packet.system or None,
        "target": context.get("target"),
        "context": context,
        "dry_run": True,
    }


class BrainAPI:
    """Run DecisionBrain and return a compact brain result."""

    def __init__(self, transport: SyncTransportProtocol) -> None:
        self._transport = transport

    def run(
        self,
        *,
        packet: DecisionPacket,
        action: Optional[str] = None,
        actor: str = "AI_AGENT",
        idempotency_key: Optional[str] = None,
    ) -> DecisionBrainResult:
        response = self._transport.request(
            method="POST",
            path="/actions/evaluate",
            json_body=_body_from_packet(packet, action=action, actor=actor),
            idempotency_key=idempotency_key,
        )
        return DecisionBrainResult.from_response(response)


class AsyncBrainAPI:
    """Async DecisionBrain runner."""

    def __init__(self, transport: AsyncTransportProtocol) -> None:
        self._transport = transport

    async def run(
        self,
        *,
        packet: DecisionPacket,
        action: Optional[str] = None,
        actor: str = "AI_AGENT",
        idempotency_key: Optional[str] = None,
    ) -> DecisionBrainResult:
        response = await self._transport.request(
            method="POST",
            path="/actions/evaluate",
            json_body=_body_from_packet(packet, action=action, actor=actor),
            idempotency_key=idempotency_key,
        )
        return DecisionBrainResult.from_response(response)
