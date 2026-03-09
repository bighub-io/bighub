from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .resources.actions import ActionsAPI
from .resources.approvals import ApprovalsAPI
from .resources.api_keys import APIKeysAPI
from .resources.auth import AuthAPI
from .resources.events import EventsAPI
from .resources.kill_switch import KillSwitchAPI
from .resources.rules import RulesAPI
from .resources.webhooks import WebhooksAPI
from .transport import RetryConfig, SyncTransport
from .version import __version__


@dataclass
class BighubClient:
    """
    Official sync client for governing AI agent execution with the BIGHUB
    intelligence and control layer.
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
        self.actions = ActionsAPI(self._transport)
        self.auth = AuthAPI(self._transport)
        self.rules = RulesAPI(self._transport)
        self.kill_switch = KillSwitchAPI(self._transport)
        self.events = EventsAPI(self._transport)
        self.approvals = ApprovalsAPI(self._transport)
        self.api_keys = APIKeysAPI(self._transport)
        self.webhooks = WebhooksAPI(self._transport)

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> "BighubClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self.close()
