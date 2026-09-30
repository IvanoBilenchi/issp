from __future__ import annotations

import contextlib
import dataclasses
import functools
import logging
import os
import sys
import threading
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from time import perf_counter_ns as tick
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Collection, Generator, Iterable, Iterator
    from typing import Any, TextIO


_LOGGER = logging.getLogger("issp")
_TAGS_ATTR = "issp_tags"

_DIM = "2"
_LEVEL_STYLES = {
    DEBUG: _DIM,
    INFO: "32",
    WARNING: "1;33",
    ERROR: "1;31",
    CRITICAL: "1;97;41",
}
_TAG_BASE_STYLES = ("36", "33", "35", "32", "34")
_TAG_STYLES = (*_TAG_BASE_STYLES, *(f"1;{s}" for s in _TAG_BASE_STYLES))


def _style(text: str, *codes: str) -> str:
    return f"\x1b[{';'.join(codes)}m{text}\x1b[0m" if codes else text


class TagFamily:
    @property
    def width(self) -> int:
        return self._width

    def __init__(self, *names: str) -> None:
        self._width = 0
        self._indices: dict[str, int] = {}
        self.register(*names)

    def __call__(self, name: str) -> Tag:
        self.register(name)
        return Tag(self, name)

    def register(self, *names: str) -> None:
        for name in names:
            self._indices.setdefault(name, len(self._indices))
        self._width = max(self._width, max((len(name) for name in names), default=0))

    def index(self, name: str) -> int:
        return self._indices[name]


@dataclasses.dataclass(frozen=True)
class Tag:
    family: TagFamily
    name: str

    @property
    def style(self) -> str:
        return _TAG_STYLES[self.family.index(self.name) % len(_TAG_STYLES)]

    def __str__(self) -> str:
        pad = max(self.family.width - len(self.name), 0)
        left = pad // 2
        return f"[{' ' * left}{self.name}{' ' * (pad - left)}]"


class _Context(threading.local):
    def __init__(self) -> None:
        self.tags: list[Tag] = []


_context = _Context()


class _Formatter(logging.Formatter):
    def __init__(self, *, color: bool) -> None:
        super().__init__()
        self.color = color

    def formatMessage(self, record: logging.LogRecord) -> str:  # noqa: N802
        tags: tuple[Tag, ...] = getattr(record, _TAGS_ATTR, ())
        level = f"[{record.levelname:<5}]"
        if not self.color:
            return " ".join((level, *(str(t) for t in tags), record.message))
        dim = (_DIM,) if record.levelno == DEBUG else ()
        level = _style(level, _LEVEL_STYLES.get(record.levelno, ""))
        tag_strs = (_style(str(t), t.style, *dim) for t in tags)
        return " ".join((level, *tag_strs, _style(record.message, *dim)))


def _enable_windows_ansi(stream: TextIO) -> bool:
    if sys.platform != "win32":
        return True
    try:
        import ctypes  # noqa: PLC0415
        import msvcrt  # noqa: PLC0415

        kernel32 = ctypes.windll.kernel32
        handle = msvcrt.get_osfhandle(stream.fileno())
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        enable_vt_processing = 0x0004
        return bool(kernel32.SetConsoleMode(handle, mode.value | enable_vt_processing))
    except Exception:
        return False


def _supports_color(stream: TextIO) -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    try:
        if not stream.isatty():
            return False
    except Exception:
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    return _enable_windows_ansi(stream)


_HANDLER = logging.StreamHandler(sys.stdout)


def _setup_logger() -> None:
    logging.addLevelName(WARNING, "WARN")
    _HANDLER.setFormatter(_Formatter(color=_supports_color(_HANDLER.stream)))
    _LOGGER.addHandler(_HANDLER)
    _LOGGER.setLevel(logging.INFO)


_setup_logger()


def _int_level(level: int | str) -> int:
    return level if isinstance(level, int) else int(getattr(logging, level.upper()))


def set_level(level: int | str) -> None:
    _LOGGER.setLevel(level)


def set_color(enabled: bool | None = None) -> None:  # noqa: FBT001
    color = _supports_color(_HANDLER.stream) if enabled is None else enabled
    _HANDLER.setFormatter(_Formatter(color=color))


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
    tags = (*_context.tags, tag) if tag else tuple(_context.tags)
    extra = {_TAGS_ATTR: tags}
    _LOGGER.log(_int_level(level), msg, *args, extra=extra, **kwargs)  # type: ignore[arg-type]


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
