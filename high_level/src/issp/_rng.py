import itertools
import os
import secrets
import string
import threading
import time
from collections.abc import Iterable, Iterator, Sequence
from typing import Any

from . import _log as log
from ._crypto import AES256, CTR, BlockCipher, StreamCipher
from ._hash import sha256
from ._util import xor
from ._verify import Hash


class RNG[SeedType: (int, bytes)]:
    VALUE_SIZE = 1

    def __next__(self) -> int:
        raise NotImplementedError

    def set_seed(self, seed: SeedType) -> None:
        raise NotImplementedError

    def __iter__(self) -> Iterator[int]:
        return self

    def byte_stream(self, size: int) -> Iterator[int]:
        if self.VALUE_SIZE == 1:
            return itertools.islice(self, size)
        while size >= self.VALUE_SIZE:
            yield from next(self).to_bytes(self.VALUE_SIZE)
            size -= self.VALUE_SIZE
        if size > 0:
            yield from next(self).to_bytes(self.VALUE_SIZE)[:size]

    def bytes(self, size: int) -> bytes:
        return bytes(self.byte_stream(size))

    def number(self, size: int = VALUE_SIZE) -> int:
        return next(self) if size == self.VALUE_SIZE else int.from_bytes(self.byte_stream(size))


class LCG(RNG[int]):
    VALUE_SIZE = 4

    def __init__(self, a: int = 16807, c: int = 0, m: int = 2**31 - 1) -> None:
        self._state = time.time_ns() % m
        self._a = a % m
        self._c = c % m
        self._m = m

    def __next__(self) -> int:
        self._state = (self._a * self._state + self._c) % self._m
        return self._state

    def set_seed(self, seed: int) -> None:
        self._state = seed % self._m


class CipherRNG(RNG[bytes]):
    def __init__(self, cipher: StreamCipher) -> None:
        self._cipher = cipher
        self._key_stream: Iterator[int] = iter(b"")
        self.set_seed(cipher.key)

    def __next__(self) -> int:
        return next(self._key_stream)

    def set_seed(self, seed: bytes) -> None:
        iv = bytes(i % 256 for i in range(self._cipher.iv_size))
        self._cipher.key = seed
        self._key_stream = self._cipher.key_stream(iv)


class HashRNG(RNG[bytes]):
    def __init__(self, hash_fn: Hash) -> None:
        self._hash = hash_fn
        self._stream = self._new_stream(int.from_bytes(os.urandom(hash_fn.code_size)))

    def __next__(self) -> int:
        return next(self._stream)

    def _new_stream(self, seed: int) -> Iterator[int]:
        while True:
            yield from self._hash.compute_code(int.to_bytes(seed, self._hash.code_size))
            seed += 1

    def set_seed(self, seed: bytes) -> None:
        self._stream = self._new_stream(int.from_bytes(seed))


class ANSIx917(RNG[bytes]):
    VALUE_SIZE = 8

    def __init__(self, cipher: BlockCipher | None = None) -> None:
        self._cipher = cipher or AES256()
        self._state = bytes(self._cipher.block_size)

    def __next__(self) -> int:
        temp = self._cipher.encrypt(time.time_ns().to_bytes(self._cipher.block_size))
        output = self._cipher.encrypt(xor(self._state, temp))
        self._state = self._cipher.encrypt(xor(output, temp))
        return int.from_bytes(output[: self.VALUE_SIZE])

    def set_seed(self, seed: bytes) -> None:
        self._cipher.key = seed


class TRNG(RNG[bytes]):
    def __next__(self) -> int:
        return os.urandom(1)[0]

    def set_seed(self, seed: bytes) -> None:
        del seed  # Unused

    def bytes(self, size: int) -> bytes:
        return os.urandom(size)

    def byte_stream(self, size: int) -> Iterator[int]:
        yield from self.bytes(size)


class Fortuna(CipherRNG):
    def __init__(
        self,
        sources: Iterable[RNG[Any]],
        pools: int = 5,
        reseed_length: int = 120,
        accumulation_rate: float = 1.0,
    ) -> None:
        super().__init__(CTR(AES256()))
        self._sources = tuple(sources)
        self._pools = tuple(bytearray() for _ in range(pools))
        self._reseed_length = reseed_length
        self._reseed_count = 0
        threading.Thread(
            target=self._accumulate_entropy,
            args=(1.0 / accumulation_rate,),
            daemon=True,
        ).start()

    def _accumulate_entropy(self, interval: float) -> None:
        while True:
            for source in self._sources:
                for pool in self._pools:
                    pool.extend(source.bytes(4))
            time.sleep(interval)

    def _key_entropy(self) -> bytes:
        entropy = bytearray()
        for i, pool in enumerate(self._pools):
            if self._reseed_count % (2**i) == 0:
                entropy.extend(sha256(pool))
                pool.clear()
        return entropy

    def _reseed(self) -> None:
        log.debug("[Fortuna] Reseeding...")
        self._reseed_count += 1
        self.set_seed(sha256(self._cipher.key + sha256(self._key_entropy())))

    def __next__(self) -> int:
        self._log_pool_sizes()
        if len(self._pools[0]) >= self._reseed_length:
            self._reseed()
        return super().__next__()

    def _log_pool_sizes(self) -> None:
        sizes = ", ".join(f"P{i}: {len(pool)} B" for i, pool in enumerate(self._pools))
        log.debug("[Fortuna] %s", sizes)


def random_bytes(size: int) -> bytes:
    return secrets.token_bytes(size)


def random_string(length: int, charset: str = string.printable) -> str:
    return "".join(secrets.choice(charset) for _ in range(length))


def random_int(min_value: int = 0, max_value: int = 2**32 - 1) -> int:
    return secrets.randbelow(max_value - min_value + 1) + min_value


def random_choice[T](sequence: Sequence[T]) -> T:
    return secrets.choice(sequence)
