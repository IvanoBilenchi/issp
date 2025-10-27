# Implement a variant of the ANSI X9.17 RNG, using AES-256 as the block cipher.
# The RNG should produce 64-bit integers.
#
# Hints:
# - The `time.time_ns()` function can be used to get the current timestamp in nanoseconds.
# - Always work with block-sized (16 bytes) chunks, and truncate the output to the required size.


import time

from issp import AES256, RNG, log, run_main


class ANSIx917(RNG[bytes]):
    VALUE_SIZE = 8

    def __init__(self) -> None:
        key = bytes(i for i in range(AES256.KEY_SIZE))
        self._cipher = AES256(key)
        self._state = bytes(self._cipher.block_size)

    def __next__(self) -> int:
        # TO-DO: Implement the ANSI X9.17 RNG algorithm.
        return 42

    def set_seed(self, seed: bytes) -> None:
        # TO-DO: Set the internal state to the given seed value.
        pass


def main() -> None:
    rng = ANSIx917()
    for i, value in enumerate(rng):
        time.sleep(0.5)
        log.info("[ANSI x9.17] Value %d: %d", i + 1, value)


if __name__ == "__main__":
    run_main(main)
