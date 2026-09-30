from __future__ import annotations

import contextlib
import dataclasses
import functools
import logging
import sys
import threading
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from time import perf_counter_ns as tick
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Collection, Generator, Iterable, Iterator
    from typing import Any


_LOGGER = logging.getLogger("issp")


class TagFamily:
    @property
    def width(self) -> int:
        return self._width

    def __init__(self, *names: str) -> None:
        self._width = 0
        self.register(*names)

    def __call__(self, name: str) -> Tag:
        self.register(name)
        return Tag(self, name)

    def register(self, *names: str) -> None:
        self._width = max(self._width, max((len(name) for name in names), default=0))


@dataclasses.dataclass(frozen=True)
class Tag:
    family: TagFamily
    name: str

    def __str__(self) -> str:
        pad = max(self.family.width - len(self.name), 0)
        left = pad // 2
        return f"[{' ' * left}{self.name}{' ' * (pad - left)}]"


class _Context(threading.local):
    def __init__(self) -> None:
        self.tags: list[Tag] = []


_context = _Context()


def _setup_logger() -> None:
    logging.addLevelName(WARNING, "WARN")
    fmt = "[%(levelname)-5s] %(message)s"
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt))
    _LOGGER.addHandler(handler)
    _LOGGER.setLevel(logging.INFO)


_setup_logger()


def _int_level(level: int | str) -> int:
    return level if isinstance(level, int) else int(getattr(logging, level.upper()))


def set_level(level: int | str) -> None:
    _LOGGER.setLevel(level)


def is_enabled(level: int | str) -> bool:
    return _LOGGER.isEnabledFor(_int_level(level))


@contextlib.contextmanager
def tagged(tag: Tag) -> Generator[None]:
    _context.tags.append(tag)
    try:
        yield
    finally:
        _context.tags.pop()


def with_level(level: int | str) -> Callable[[Any], Any] | None:
    return functools.partial(log, level) if is_enabled(level) else None


def log(
    level: int | str,
    msg: str,
    *args: object,
    tag: Tag | None = None,
    **kwargs: object,
) -> None:
    tags = [*_context.tags, tag] if tag else _context.tags
    if tags:
        prefix = " ".join(str(t) for t in tags)
        msg = f"{prefix.replace('%', '%%') if args else prefix} {msg}"
    _LOGGER.log(_int_level(level), msg, *args, **kwargs)  # type: ignore[arg-type]


def debug(msg: str, *args: object, tag: Tag | None = None, **kwargs: object) -> None:
    log(DEBUG, msg, *args, tag=tag, **kwargs)


def info(msg: str, *args: object, tag: Tag | None = None, **kwargs: object) -> None:
    log(INFO, msg, *args, tag=tag, **kwargs)


def warning(msg: str, *args: object, tag: Tag | None = None, **kwargs: object) -> None:
    log(WARNING, msg, *args, tag=tag, **kwargs)


def error(msg: str, *args: object, tag: Tag | None = None, **kwargs: object) -> None:
    log(ERROR, msg, *args, tag=tag, **kwargs)


def critical(msg: str, *args: object, tag: Tag | None = None, **kwargs: object) -> None:
    log(CRITICAL, msg, *args, tag=tag, **kwargs)


def _format_time(nanos: int) -> str:
    units = ("ns", "μs", "ms", "s")
    interval: float = nanos
    while interval >= 10**3 and len(units) > 1:
        interval /= 10**3
        units = units[1:]
    return f"{interval:.2f} {units[0]}"


def _format_progress(progress: str, current: str | None, desc: str | None) -> str:
    desc = desc or "Progress"
    return f"{desc}: {progress} ({current})" if current else f"{desc}: {progress}"


def percent[T](
    collection: Collection[T],
    desc: str | None = None,
    *,
    print_current: bool = True,
) -> Iterator[T]:
    first_timestamp = tick()
    last_timestamp = first_timestamp
    length = len(collection)
    progress = 0
    for i, item in enumerate(collection):
        cur_timestamp = tick()
        new_progress = int(i / length * 100)
        if cur_timestamp - last_timestamp > 10**9 and new_progress != progress:
            last_timestamp = cur_timestamp
            progress = new_progress
            info(_format_progress(f"{progress}%", str(item) if print_current else None, desc))
        yield item
    info(_format_progress(f"100% ({_format_time(tick() - first_timestamp)})", None, desc))


def progress[T](
    iterable: Iterable[T],
    desc: str | None = None,
    *,
    print_current: bool = True,
) -> Iterator[T]:
    first_timestamp = tick()
    last_timestamp = first_timestamp
    i = 0
    try:
        for i, item in enumerate(iterable):
            if (cur_timestamp := tick()) - last_timestamp > 10**9:
                last_timestamp = cur_timestamp
                info(_format_progress(f"{i}", str(item) if print_current else None, desc))
            yield item
    finally:
        info(_format_progress(f"done ({i}, {_format_time(tick() - first_timestamp)})", None, desc))
