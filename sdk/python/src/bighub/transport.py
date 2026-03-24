from __future__ import annotations

import asyncio
import ipaddress
import logging
import os
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx

from .auth import build_auth_headers
from .exceptions import (
    BighubAPIError,
    BighubAuthError,
    BighubNetworkError,
    BighubRateLimitError,
    BighubTimeoutError,
    BighubValidationError,
)

logger = logging.getLogger("bighub")


def _join_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def _validate_base_url(base_url: str) -> None:
    parsed = urlparse(base_url)
    scheme = (parsed.scheme or "").lower()
    host = (parsed.hostname or "").lower()
    allow_insecure = os.getenv("BIGHUB_ALLOW_INSECURE_HTTP", "").strip().lower() in {"1", "true", "yes", "on"}
    localhost = host in {"localhost", "127.0.0.1"}
    private_host = False
    try:
        ip = ipaddress.ip_address(host)
        private_host = ip.is_private or ip.is_loopback
    except ValueError:
        private_host = host.endswith(".local")

    if scheme != "https" and not (localhost or (allow_insecure and private_host)):
        raise ValueError(
            "Insecure base_url is not allowed. Use https:// or set "
            "BIGHUB_ALLOW_INSECURE_HTTP=true only for localhost/private hosts."
        )


def _should_retry(status_code: Optional[int], exc: Optional[Exception]) -> bool:
    if exc is not None:
        return isinstance(exc, (httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError))
    if status_code is None:
        return False
    return status_code in (408, 409, 425, 429) or 500 <= status_code <= 599


@dataclass
class RetryConfig:
    max_retries: int = 2
    backoff_base: float = 0.25
    backoff_cap: float = 2.5

    def backoff(self, attempt: int) -> float:
        # Exponential backoff + bounded jitter.
        delay = min(self.backoff_cap, self.backoff_base * (2 ** max(0, attempt - 1)))
        return delay + random.uniform(0.0, min(0.25, delay / 2))


def build_headers(
    *,
    api_key: Optional[str],
    bearer_token: Optional[str],
    user_agent: str,
    extra_headers: Optional[Dict[str, str]] = None,
    idempotency_key: Optional[str] = None,
) -> Dict[str, str]:
    headers = {"User-Agent": user_agent, "Accept": "application/json"}
    headers.update(build_auth_headers(api_key=api_key, bearer_token=bearer_token))
    if extra_headers:
        headers.update(extra_headers)
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    return headers


def parse_response_or_raise(response: httpx.Response) -> Dict[str, Any]:
    content_type = response.headers.get("content-type", "")
    body: Dict[str, Any] = {}
    if "application/json" in content_type:
        try:
            body = response.json()
        except Exception:
            body = {}

    if 200 <= response.status_code < 300:
        return body

    if response.status_code in (401, 403):
        detail = body.get("detail") if isinstance(body, dict) else None
        raise BighubAuthError(str(detail or "Unauthorized"))

    detail = body.get("detail") if isinstance(body, dict) else None
    request_id = None
    if isinstance(body, dict):
        request_id = body.get("request_id") or body.get("validation_id")
        if not request_id:
            err = body.get("error")
            if isinstance(err, dict):
                request_id = err.get("request_id")
    code = None
    if isinstance(detail, dict):
        code = detail.get("code")

    base_kwargs = dict(
        message=response.reason_phrase or "API error",
        status_code=response.status_code,
        request_id=request_id,
        code=code,
        detail=detail,
        response_body=body if body else None,
    )

    if response.status_code == 429:
        retry_after: Optional[float] = None
        raw = response.headers.get("retry-after")
        if raw:
            try:
                retry_after = float(raw)
            except (ValueError, TypeError):
                pass
        raise BighubRateLimitError(**base_kwargs, retry_after_seconds=retry_after)

    if response.status_code == 422:
        validation_errors = []
        if isinstance(detail, list):
            validation_errors = detail
        elif isinstance(body, dict) and isinstance(body.get("detail"), list):
            validation_errors = body["detail"]
        raise BighubValidationError(**base_kwargs, validation_errors=validation_errors)

    raise BighubAPIError(**base_kwargs)


class SyncTransport:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: Optional[str],
        bearer_token: Optional[str],
        timeout: float,
        retry: RetryConfig,
        user_agent: str,
    ) -> None:
        _validate_base_url(base_url)
        self.base_url = base_url
        self.api_key = api_key
        self.bearer_token = bearer_token
        self.timeout = timeout
        self.retry = retry
        self.user_agent = user_agent
        self._client = httpx.Client(timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def request(
        self,
        *,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        url = _join_url(self.base_url, path)
        req_headers = build_headers(
            api_key=self.api_key,
            bearer_token=self.bearer_token,
            user_agent=self.user_agent,
            extra_headers=headers,
            idempotency_key=idempotency_key,
        )

        last_exc: Optional[Exception] = None
        for attempt in range(1, self.retry.max_retries + 2):
            status_code: Optional[int] = None
            t0 = time.monotonic()
            try:
                logger.debug("BIGHUB %s %s attempt=%d", method.upper(), path, attempt)
                response = self._client.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=json_body,
                    headers=req_headers,
                )
                status_code = response.status_code
                elapsed = time.monotonic() - t0
                logger.debug("BIGHUB %s %s → %d (%.3fs)", method.upper(), path, status_code, elapsed)
                if _should_retry(status_code=status_code, exc=None) and attempt <= self.retry.max_retries:
                    backoff = self.retry.backoff(attempt)
                    logger.warning("BIGHUB retry %d/%d %s %s (status=%d) in %.2fs", attempt, self.retry.max_retries, method.upper(), path, status_code, backoff)
                    time.sleep(backoff)
                    continue
                return parse_response_or_raise(response)
            except httpx.TimeoutException as exc:
                logger.warning("BIGHUB timeout %s %s attempt=%d: %s", method.upper(), path, attempt, exc)
                if attempt <= self.retry.max_retries:
                    time.sleep(self.retry.backoff(attempt))
                    continue
                raise BighubTimeoutError(f"Request timed out: {method.upper()} {path}") from exc
            except httpx.RequestError as exc:
                last_exc = exc
                logger.warning("BIGHUB network error %s %s attempt=%d: %s", method.upper(), path, attempt, exc)
                if _should_retry(status_code=status_code, exc=exc) and attempt <= self.retry.max_retries:
                    time.sleep(self.retry.backoff(attempt))
                    continue
                raise BighubNetworkError(f"Network error: {method.upper()} {path}") from exc

        raise BighubNetworkError(f"Request failed after retries: {method.upper()} {path}") from last_exc


class AsyncTransport:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: Optional[str],
        bearer_token: Optional[str],
        timeout: float,
        retry: RetryConfig,
        user_agent: str,
    ) -> None:
        _validate_base_url(base_url)
        self.base_url = base_url
        self.api_key = api_key
        self.bearer_token = bearer_token
        self.timeout = timeout
        self.retry = retry
        self.user_agent = user_agent
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        await self._client.aclose()

    async def request(
        self,
        *,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        url = _join_url(self.base_url, path)
        req_headers = build_headers(
            api_key=self.api_key,
            bearer_token=self.bearer_token,
            user_agent=self.user_agent,
            extra_headers=headers,
            idempotency_key=idempotency_key,
        )

        last_exc: Optional[Exception] = None
        for attempt in range(1, self.retry.max_retries + 2):
            status_code: Optional[int] = None
            t0 = time.monotonic()
            try:
                logger.debug("BIGHUB %s %s attempt=%d", method.upper(), path, attempt)
                response = await self._client.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=json_body,
                    headers=req_headers,
                )
                status_code = response.status_code
                elapsed = time.monotonic() - t0
                logger.debug("BIGHUB %s %s → %d (%.3fs)", method.upper(), path, status_code, elapsed)
                if _should_retry(status_code=status_code, exc=None) and attempt <= self.retry.max_retries:
                    backoff = self.retry.backoff(attempt)
                    logger.warning("BIGHUB retry %d/%d %s %s (status=%d) in %.2fs", attempt, self.retry.max_retries, method.upper(), path, status_code, backoff)
                    await asyncio.sleep(backoff)
                    continue
                return parse_response_or_raise(response)
            except httpx.TimeoutException as exc:
                logger.warning("BIGHUB timeout %s %s attempt=%d: %s", method.upper(), path, attempt, exc)
                if attempt <= self.retry.max_retries:
                    await asyncio.sleep(self.retry.backoff(attempt))
                    continue
                raise BighubTimeoutError(f"Request timed out: {method.upper()} {path}") from exc
            except httpx.RequestError as exc:
                last_exc = exc
                logger.warning("BIGHUB network error %s %s attempt=%d: %s", method.upper(), path, attempt, exc)
                if _should_retry(status_code=status_code, exc=exc) and attempt <= self.retry.max_retries:
                    await asyncio.sleep(self.retry.backoff(attempt))
                    continue
                raise BighubNetworkError(f"Network error: {method.upper()} {path}") from exc

        raise BighubNetworkError(f"Request failed after retries: {method.upper()} {path}") from last_exc
