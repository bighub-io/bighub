from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any, Dict, Union


def verify_chronos_signature(
    *,
    payload: Union[str, bytes, Dict[str, Any]],
    signature: str,
    secret: str,
    timestamp: int,
    tolerance_seconds: int = 300,
) -> bool:
    """
    Verify BIGHUB webhook signature header format:
    v1=HMAC_SHA256(secret, "{timestamp}.{payload}")
    """
    now = int(time.time())
    if abs(now - timestamp) > tolerance_seconds:
        return False

    if isinstance(payload, dict):
        payload_text = json.dumps(payload, separators=(",", ":"), default=str)
    elif isinstance(payload, bytes):
        payload_text = payload.decode("utf-8")
    else:
        payload_text = payload

    message = f"{timestamp}.{payload_text}".encode("utf-8")
    expected = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, f"v1={expected}")
