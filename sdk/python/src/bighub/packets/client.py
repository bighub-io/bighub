from __future__ import annotations

from typing import Any, Optional

from ..types import JSONDict
from .types import DecisionPacket


class PacketsAPI:
    """Build Decision Packets locally before a decision is evaluated."""

    def build(
        self,
        *,
        action: str,
        context: Optional[JSONDict] = None,
        objective: str = "better_decision",
        system: Optional[str] = None,
        environment: Optional[str] = None,
        constraints: Optional[list[Any]] = None,
        candidate_actions: Optional[list[Any]] = None,
    ) -> DecisionPacket:
        return DecisionPacket.build(
            action=action,
            context=context,
            objective=objective,
            system=system,
            environment=environment,
            constraints=constraints,
            candidate_actions=candidate_actions,
        )


class AsyncPacketsAPI(PacketsAPI):
    async def build(self, **kwargs: Any) -> DecisionPacket:  # type: ignore[override]
        return super().build(**kwargs)
