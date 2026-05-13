from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from ..types import JSONDict

F = TypeVar("F", bound=Callable[..., Any])


def action(
    *,
    system: str,
    risk: str = "",
    environment: str = "",
    context: Optional[JSONDict] = None,
) -> Callable[[F], F]:
    """Attach BIGHUB action metadata to an existing workflow function.

    The decorator is intentionally light: it does not execute BIGHUB on its own.
    Runtimes and adapters can read ``__bighub_action__`` and call
    ``bighub.decide(...)`` before invoking the function.
    """

    def decorate(fn: F) -> F:
        metadata = {
            "system": system,
            "risk": risk,
            "environment": environment,
            "context": dict(context or {}),
        }
        setattr(fn, "__bighub_action__", metadata)

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return fn(*args, **kwargs)

        setattr(wrapper, "__bighub_action__", metadata)
        return wrapper  # type: ignore[return-value]

    return decorate
