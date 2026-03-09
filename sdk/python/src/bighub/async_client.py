from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .resources.actions import AsyncActionsAPI
from .resources.approvals import AsyncApprovalsAPI
from .resources.api_keys import AsyncAPIKeysAPI
from .resources.auth import AsyncAuthAPI
from .resources.events import AsyncEventsAPI
from .resources.kill_switch import AsyncKillSwitchAPI
from .resources.rules import AsyncRulesAPI
from .resources.webhooks import AsyncWebhooksAPI
from .transport import AsyncTransport, RetryConfig
from .version import __version__


@dataclass
class AsyncBighubClient:
    """
    Official async client for governing AI agent execution with the BIGHUB
    intelligence and control layer.
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
        self.actions = AsyncActionsAPI(self._transport)
        self.auth = AsyncAuthAPI(self._transport)
        self.rules = AsyncRulesAPI(self._transport)
        self.kill_switch = AsyncKillSwitchAPI(self._transport)
        self.events = AsyncEventsAPI(self._transport)
        self.approvals = AsyncApprovalsAPI(self._transport)
        self.api_keys = AsyncAPIKeysAPI(self._transport)
        self.webhooks = AsyncWebhooksAPI(self._transport)

    async def close(self) -> None:
        await self._transport.close()

    async def __aenter__(self) -> "AsyncBighubClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        await self.close()
