from __future__ import annotations

import functools
import logging
import sys
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any


_LOGGER = logging.getLogger("issp")


def _setup_logger() -> None:
    fmt = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
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
