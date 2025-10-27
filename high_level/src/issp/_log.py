from __future__ import annotations

import functools
import logging
import sys
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from time import perf_counter_ns as tick
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Collection, Iterable, Iterator
    from typing import Any


_LOGGER = logging.getLogger("issp")


def _setup_logger() -> None:
    logging.addLevelName(WARNING, "WARN")
    fmt = "[%(asctime)s] [%(name)s] [%(levelname)-5s] %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    _LOGGER.addHandler(handler)
    _LOGGER.setLevel(logging.INFO)


_setup_logger()


def _int_level(level: int | str) -> int:
    return level if isinstance(level, int) else int(getattr(logging, level.upper()))


def set_level(level: int | str) -> None:
    _LOGGER.setLevel(level)


def with_level(level: int | str) -> Callable[[Any], Any] | None:
    return functools.partial(log, level) if _LOGGER.isEnabledFor(_int_level(level)) else None


def log(level: int | str, msg: str, *args: object, **kwargs: object) -> None:
    _LOGGER.log(_int_level(level), msg, *args, **kwargs)  # type: ignore[arg-type]


def debug(msg: str, *args: object, **kwargs: object) -> None:
    log(DEBUG, msg, *args, **kwargs)


def info(msg: str, *args: object, **kwargs: object) -> None:
    log(INFO, msg, *args, **kwargs)


def warning(msg: str, *args: object, **kwargs: object) -> None:
    log(WARNING, msg, *args, **kwargs)


def error(msg: str, *args: object, **kwargs: object) -> None:
    log(ERROR, msg, *args, **kwargs)


def critical(msg: str, *args: object, **kwargs: object) -> None:
    log(CRITICAL, msg, *args, **kwargs)


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
