from __future__ import annotations

from .sync_client import BighubClient


class Bighub(BighubClient):
    """Modern public SDK entrypoint.

    Prefer ``Bighub(...).decide(...)`` for new integrations. ``BighubClient``
    remains available for backward compatibility.
    """


__all__ = ["Bighub"]
