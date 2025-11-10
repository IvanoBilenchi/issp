from collections.abc import Callable

from . import _log as log


def run_main(fn: Callable[..., None]) -> None:
    try:
        fn()
    except KeyboardInterrupt:
        log.info("Interrupted by user, exiting.")
    except Exception as e:
        log.error("%s: %s", type(e).__name__, e)
