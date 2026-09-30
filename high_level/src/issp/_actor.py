from __future__ import annotations

import contextlib
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

_state = threading.local()


def current() -> str | None:
    """
    Get the name of the actor running in the current thread.

    :return: The name of the actor, or None if the current thread is not an actor thread.
    """
    return getattr(_state, "name", None)


@contextlib.contextmanager
def acting_as(name: str) -> Generator[None]:
    """
    Run the enclosed code as the specified actor in the current thread.

    :param name: The name of the actor.
    """
    previous = current()
    _state.name = name
    try:
        yield
    finally:
        _state.name = previous
