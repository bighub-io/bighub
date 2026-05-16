from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .brain import BrainAPI
from .decisions import DecisionsAPI
from .resources.actions import ActionsAPI
from .resources.approvals import ApprovalsAPI
from .resources.api_keys import APIKeysAPI
from .resources.auth import AuthAPI
from .resources.calibration import CalibrationAPI
from .resources.cases import CasesAPI
from .resources.events import EventsAPI
from .resources.features import FeaturesAPI
from .resources.ingest import IngestAPI
from .resources.insights import InsightsAPI
from .resources.kill_switch import KillSwitchAPI
from .resources.learning import LearningAPI
from .resources.noosphere import NoosphereAPI
from .resources.outcomes import OutcomesAPI
from .resources.precedents import PrecedentsAPI
from .resources.retrieval import RetrievalAPI
from .resources.rules import ConstraintsAPI
from .resources.simulations import SimulationsAPI
from .resources.webhooks import WebhooksAPI
from .packets import PacketsAPI
from .reviews import ReviewsAPI
from .systems import SystemsAPI
from .transport import RetryConfig, SyncTransport
from .types import JSONDict
from .version import __version__


@dataclass
class BighubClient:
    """
    Official sync client for the BIGHUB decision learning platform.

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
        self._transport = SyncTransport(
            base_url=self.base_url,
            api_key=self.api_key,
            bearer_token=self.bearer_token,
            timeout=self.timeout,
            retry=RetryConfig(max_retries=self.max_retries),
            user_agent=self.user_agent or f"bighub-python/{__version__}",
        )
        # Core decision loop
        self.actions = ActionsAPI(self._transport)
        self.cases = CasesAPI(self._transport)
        self.outcomes = OutcomesAPI(self._transport)
        self.ingest = IngestAPI(self._transport)

        # Better Decision SDK surface
        self.reviews = ReviewsAPI(self._transport)
        self.decisions = DecisionsAPI(self._transport, reviews=self.reviews, outcomes=self.outcomes)
        self.packets = PacketsAPI()
        self.brain = BrainAPI(self._transport)
        self.systems = SystemsAPI(self._transport)

        # Decision learning
        self.precedents = PrecedentsAPI(self._transport)
        self.calibration = CalibrationAPI(self._transport)
        self.retrieval = RetrievalAPI(self._transport)
        self.insights = InsightsAPI(self._transport)
        self.features = FeaturesAPI(self._transport)
        self.simulations = SimulationsAPI(self._transport)
        self.learning = LearningAPI(self._transport)
        self.noosphere = NoosphereAPI(self._transport)

        # Configuration and controls
        self.constraints = ConstraintsAPI(self._transport)
        self.rules = self.constraints  # backward-compatible alias
        self.kill_switch = KillSwitchAPI(self._transport)
        self.approvals = ApprovalsAPI(self._transport)

        # Platform
        self.auth = AuthAPI(self._transport)
        self.events = EventsAPI(self._transport)
        self.api_keys = APIKeysAPI(self._transport)
        self.webhooks = WebhooksAPI(self._transport)

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> "BighubClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self.close()

    def decide(
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
        return self.decisions.evaluate(
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

    def build_packet(self, **kwargs):  # type: ignore[no-untyped-def]
        return self.packets.build(**kwargs)

    def run_brain(self, **kwargs):  # type: ignore[no-untyped-def]
        return self.brain.run(**kwargs)
