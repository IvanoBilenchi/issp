# Implement a variant of the ANSI X9.17 RNG, using AES-256 as the block cipher.
#
# Hints:
# - The RNG should produce 64-bit integers, as denoted by the `VALUE_SIZE` attribute.
# - The `time.time_ns()` function can be used to get the current timestamp in nanoseconds.
# - Always work with block-sized (16 bytes) chunks, and truncate the output to the required size.


import time

from issp import AES256, RNG, log, xor


class ANSIx917(RNG[bytes]):
    VALUE_SIZE = 8

    def __init__(self) -> None:
        key = bytes(i for i in range(AES256.KEY_SIZE))
        self._cipher = AES256(key)
        self._state = bytes(self._cipher.block_size)

    def __next__(self) -> int:
        temp = self._cipher.encrypt(time.time_ns().to_bytes(self._cipher.block_size))
        output = self._cipher.encrypt(xor(self._state, temp))
        self._state = self._cipher.encrypt(xor(output, temp))
        return int.from_bytes(output[: self.VALUE_SIZE])

    def set_seed(self, seed: bytes) -> None:
        self._cipher.key = seed


def main() -> None:
    rng = ANSIx917()
    for i, value in enumerate(rng):
        time.sleep(0.5)
        log.info("[ANSI x9.17] Value %d: %d", i + 1, value)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("Interrupted by user, exiting.")
