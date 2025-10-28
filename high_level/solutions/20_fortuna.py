# Implement the Fortuna RNG, using AES-256 as the block cipher and SHA-256 as the hash function.
# The RNG should produce 64-bit integers, use 5 entropy pools, and reseed when pool 0
# accumulates at least 80 bytes of data.
#
# Hints:
# - Entropy sources are approximated using multiple `TRNG` instances. You can extract
#   random bytes from these sources using their `bytes` method.
# - Entropy pools can be seen as bytearrays that accumulate data from the entropy sources.
# - When using a pool for reseeding, make sure to deskew it by hashing its content, then clear it.

import threading
import time
from collections.abc import Iterable
from typing import Any

from issp import AES256, RNG, TRNG, log, run_main, sha256


class Fortuna(RNG[bytes]):
    VALUE_SIZE = 8
    POOLS = 5
    RESEED_SIZE = 80

    def __init__(self, sources: Iterable[RNG[Any]]) -> None:
        key = bytes(i for i in range(AES256.KEY_SIZE))
        self.cipher = AES256(key)
        self.sources = list(sources)
        self.pools = [bytearray() for _ in range(self.POOLS)]
        self.reseed_count = 0
        self.ctr_counter = 12345
        threading.Thread(target=self._accumulate_entropy, daemon=True).start()

    def _accumulate_entropy(self) -> None:
        while True:
            for source in self.sources:
                for pool in self.pools:
                    pool.extend(source.bytes(4))
            time.sleep(1.0)

    def _reseed(self) -> None:
        self.reseed_count += 1
        log.debug("[Fortuna] Reseed %d...", self.reseed_count)

        # Accumulate entropy from a subset of the pools.
        entropy = bytearray()
        for i, pool in enumerate(self.pools):
            if self.reseed_count % (2**i) == 0:
                entropy.extend(sha256(pool))
                pool.clear()

        # Set the new seed.
        self.set_seed(sha256(self.cipher.key + sha256(entropy)))

    def __next__(self) -> int:
        self._log_pool_sizes()

        # Reseed if enough data is in pool 0.
        if len(self.pools[0]) >= self.RESEED_SIZE:
            self._reseed()

        # Generate output.
        output = self.cipher.encrypt(self.ctr_counter.to_bytes(self.cipher.block_size))
        self.ctr_counter += 1
        return int.from_bytes(output[: self.VALUE_SIZE])

    def _log_pool_sizes(self) -> None:
        sizes = ", ".join(f"P{i}: {len(pool)} B" for i, pool in enumerate(self.pools))
        log.debug("[Fortuna] %s", sizes)

    def set_seed(self, seed: bytes) -> None:
        self.cipher.key = seed


def main() -> None:
    log.set_level(log.DEBUG)
    sources = [TRNG() for _ in range(5)]
    rng = Fortuna(sources)
    for i, value in enumerate(rng):
        time.sleep(1.0)
        log.info("[Fortuna] Value %d: %d", i + 1, value)


if __name__ == "__main__":
    run_main(main)
