from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


class BighubError(Exception):
    """Base SDK error."""


class BighubAuthError(BighubError):
    """Authentication or authorization error."""


class BighubTimeoutError(BighubError):
    """Request timeout."""


class BighubNetworkError(BighubError):
    """Network-level request error."""


@dataclass
class BighubAPIError(BighubError):
    """HTTP API error with structured metadata."""

    message: str
    status_code: int
    request_id: Optional[str] = None
    code: Optional[str] = None
    detail: Optional[Any] = None
    response_body: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        base = f"{self.status_code} {self.message}"
        if self.code:
            base = f"{base} (code={self.code})"
        if self.request_id:
            base = f"{base} [request_id={self.request_id}]"
        return base
