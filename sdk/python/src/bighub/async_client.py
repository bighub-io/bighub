from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .brain import AsyncBrainAPI
from .decisions import AsyncDecisionsAPI
from .packets import AsyncPacketsAPI
from .resources.actions import AsyncActionsAPI
from .resources.approvals import AsyncApprovalsAPI
from .resources.api_keys import AsyncAPIKeysAPI
from .resources.auth import AsyncAuthAPI
from .resources.calibration import AsyncCalibrationAPI
from .resources.cases import AsyncCasesAPI
from .resources.events import AsyncEventsAPI
from .resources.features import AsyncFeaturesAPI
from .resources.ingest import AsyncIngestAPI
from .resources.insights import AsyncInsightsAPI
from .resources.kill_switch import AsyncKillSwitchAPI
from .resources.learning import AsyncLearningAPI
from .resources.noosphere import AsyncNoosphereAPI
from .resources.outcomes import AsyncOutcomesAPI
from .resources.precedents import AsyncPrecedentsAPI
from .resources.retrieval import AsyncRetrievalAPI
from .resources.rules import AsyncConstraintsAPI
from .resources.simulations import AsyncSimulationsAPI
from .resources.webhooks import AsyncWebhooksAPI
from .reviews import AsyncReviewsAPI
from .systems import AsyncSystemsAPI
from .transport import AsyncTransport, RetryConfig
from .types import JSONDict
from .version import __version__


@dataclass
class AsyncBighubClient:
    """
    Official async client for the BIGHUB decision learning platform.

    Evaluate agent actions before execution, report real outcomes,
    and let the system learn from experience.
    """

    base_url: str = "https://api.bighub.io"
    api_key: Optional[str] = None
    bearer_token: Optional[str] = None
    timeout: float = 15.0
    max_retries: int = 2
    user_agent: Optional[str] = None

    def __post_init__(self) -> None:
        self._transport = AsyncTransport(
            base_url=self.base_url,
            api_key=self.api_key,
            bearer_token=self.bearer_token,
            timeout=self.timeout,
            retry=RetryConfig(max_retries=self.max_retries),
            user_agent=self.user_agent or f"bighub-python/{__version__}",
        )
        # Core decision loop
        self.actions = AsyncActionsAPI(self._transport)
        self.cases = AsyncCasesAPI(self._transport)
        self.outcomes = AsyncOutcomesAPI(self._transport)
        self.ingest = AsyncIngestAPI(self._transport)

        # Better Decision SDK surface
        self.reviews = AsyncReviewsAPI(self._transport)
        self.decisions = AsyncDecisionsAPI(self._transport, reviews=self.reviews, outcomes=self.outcomes)
        self.packets = AsyncPacketsAPI()
        self.brain = AsyncBrainAPI(self._transport)
        self.systems = AsyncSystemsAPI(self._transport)

        # Decision learning
        self.precedents = AsyncPrecedentsAPI(self._transport)
        self.calibration = AsyncCalibrationAPI(self._transport)
        self.retrieval = AsyncRetrievalAPI(self._transport)
        self.insights = AsyncInsightsAPI(self._transport)
        self.features = AsyncFeaturesAPI(self._transport)
        self.simulations = AsyncSimulationsAPI(self._transport)
        self.learning = AsyncLearningAPI(self._transport)
        self.noosphere = AsyncNoosphereAPI(self._transport)

        # Configuration and controls
        self.constraints = AsyncConstraintsAPI(self._transport)
        self.rules = self.constraints  # backward-compatible alias
        self.kill_switch = AsyncKillSwitchAPI(self._transport)
        self.approvals = AsyncApprovalsAPI(self._transport)

        # Platform
        self.auth = AsyncAuthAPI(self._transport)
        self.events = AsyncEventsAPI(self._transport)
        self.api_keys = AsyncAPIKeysAPI(self._transport)
        self.webhooks = AsyncWebhooksAPI(self._transport)

    async def close(self) -> None:
        await self._transport.close()

    async def __aenter__(self) -> "AsyncBighubClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        await self.close()

    async def decide(
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
    ):
        """Turn a proposed IT agent action into a better decision before it runs."""
        return await self.decisions.evaluate(
            action=action,
            context=context,
            objective=objective,
            model_selection=model_selection,
            value=value,
            target=target,
            actor=actor,
            domain=domain,
            dry_run=dry_run,
            idempotency_key=idempotency_key,
            raw=raw,
        )

    async def build_packet(self, **kwargs):  # type: ignore[no-untyped-def]
        return await self.packets.build(**kwargs)

    async def run_brain(self, **kwargs):  # type: ignore[no-untyped-def]
        return await self.brain.run(**kwargs)
