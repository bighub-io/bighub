from __future__ import annotations

from typing import Dict, Optional


def build_auth_headers(
    *,
    api_key: Optional[str],
    bearer_token: Optional[str],
) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if api_key:
        headers["X-API-Key"] = api_key
    elif bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    return headers
