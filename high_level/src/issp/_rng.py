import itertools
import threading
import time
from collections.abc import Iterable, Iterator
from typing import Any

from ._bytes import byte_size, xor
from ._crypto import AES128, CTR, BlockCipher, StreamCipher
from ._hash import sha256
from ._random import random_bytes
from ._verify import HMAC, SHA1, Hash


class RNG[SeedType: (int, bytes)]:
    """Base class for random number generators."""

    @property
    def value_size(self) -> int:
        """
        Get the size of the values produced by the RNG in bytes.

        :return: The size of the values in bytes.
        """
        return getattr(self.__class__, "VALUE_SIZE", 1)

    def __next__(self) -> int:
        """
        Return the next random value.

        :return: The next random value.
        """
        raise NotImplementedError

    def set_seed(self, seed: SeedType) -> None:
        """
        Set the seed for the RNG.

        :param seed: The seed value.
        """
        raise NotImplementedError

    def __iter__(self) -> Iterator[int]:
        return self

    def byte_stream(self, size: int | None = None) -> Iterator[int]:
        """
        Generate a stream of random bytes.

        :param size: The number of bytes to generate. If None, generates an infinite stream.
        :return: An iterator of random bytes.
        """
        if size is not None and size <= 0:
            return

        if self.value_size == 1:
            if size is None:
                yield from self
            else:
                yield from itertools.islice(self, size)
            return

        if size is None:
            while True:
                yield from next(self).to_bytes(self.value_size)

        while size >= self.value_size:
            yield from next(self).to_bytes(self.value_size)
            size -= self.value_size

        if size > 0:
            yield from next(self).to_bytes(self.value_size)[:size]

    def bytes(self, size: int) -> bytes:
        """
        Generate random bytes.

        :param size: The number of bytes to generate.
        :return: A bytes object containing random bytes.
        """
        return bytes(self.byte_stream(size))

    def number(self, size: int | None = None) -> int:
        """
        Generate a random integer of the specified byte size.

        :param size: The byte size of the integer. If None, uses the RNG's value size.
        :return: A random integer.
        """
        size = size or self.value_size
        return next(self) if size == self.value_size else int.from_bytes(self.byte_stream(size))


class LCG(RNG[int]):
    """Linear Congruential Generator RNG."""

    @property
    def value_size(self) -> int:
        return byte_size(self._m)

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
    """RNG based on a stream cipher."""

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
    """RNG based on a hash function."""

    def __init__(self, hash_fn: Hash) -> None:
        self._hash = hash_fn
        self._stream = self._new_stream(int.from_bytes(random_bytes(hash_fn.code_size)))

    def __next__(self) -> int:
        return next(self._stream)

    def _new_stream(self, seed: int) -> Iterator[int]:
        while True:
            yield from self._hash.compute_code(int.to_bytes(seed, self._hash.code_size))
            seed += 1

    def set_seed(self, seed: bytes) -> None:
        self._stream = self._new_stream(int.from_bytes(seed))


class ANSIx917(RNG[bytes]):
    """ANSI X9.17 RNG."""

    VALUE_SIZE = 8

    def __init__(self, cipher: BlockCipher | None = None) -> None:
        self._cipher = cipher or AES128()
        self._state = bytes(self._cipher.block_size)

    def __next__(self) -> int:
        temp = self._cipher.encrypt(time.time_ns().to_bytes(self._cipher.block_size))
        output = self._cipher.encrypt(xor(self._state, temp))
        self._state = self._cipher.encrypt(xor(output, temp))
        return int.from_bytes(output[: self.value_size])

    def set_seed(self, seed: bytes) -> None:
        self._cipher.key = seed


class TRNG(RNG[bytes]):
    """True Random Number Generator."""

    @staticmethod
    def _random_stream() -> Iterator[int]:
        while True:
            yield from random_bytes(1024)

    def __init__(self) -> None:
        super().__init__()
        self._stream = self._random_stream()

    def __next__(self) -> int:
        return next(self._stream)

    def set_seed(self, seed: bytes) -> None:
        del seed  # Unused


class Fortuna(CipherRNG):
    """Fortuna RNG."""

    def __init__(
        self,
        sources: Iterable[RNG[Any]],
        pools: int = 5,
        reseed_length: int = 120,
        accumulation_rate: float = 1.0,
    ) -> None:
        super().__init__(CTR(AES128()))
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
        self._reseed_count += 1
        self.set_seed(sha256(self._cipher.key + sha256(self._key_entropy())))

    def __next__(self) -> int:
        if len(self._pools[0]) >= self._reseed_length:
            self._reseed()
        return super().__next__()


class OTP(RNG[int]):
    """Base class for One-Time Password (OTP) generators."""

    @property
    def value_size(self) -> int:
        return byte_size(10**self.digits - 1)

    @property
    def digits(self) -> int:
        return getattr(self, "_digits", 6)


class HOTP(OTP):
    """HMAC-based One-Time Password (HOTP) generator."""

    @staticmethod
    def code(hmac: HMAC, counter: int, digits: int = 6) -> int:
        if digits < 1 or digits > 10:  # noqa: PLR2004
            err_msg = "Digits must be between 1 and 10"
            raise ValueError(err_msg)
        mac = hmac.compute_code(counter.to_bytes(8))
        offset = mac[-1] & 0x0F
        code = (
            ((mac[offset] & 0x7F) << 24)
            | ((mac[offset + 1] & 0xFF) << 16)
            | ((mac[offset + 2] & 0xFF) << 8)
            | (mac[offset + 3] & 0xFF)
        )
        return code % (10**digits)

    def __init__(self, key: bytes, digits: int = 6, counter: int = 0) -> None:
        self._hmac = HMAC(SHA1(), key)
        self._digits = max(1, min(10, digits))
        self._counter = max(0, counter)

    def __next__(self) -> int:
        code = self.code(self._hmac, self._counter, self._digits)
        self._counter += 1
        return code

    def set_seed(self, seed: int) -> None:
        self._counter = seed


class TOTP(RNG[int]):
    """Time-based One-Time Password (TOTP) generator."""

    def __init__(self, key: bytes, digits: int = 6, period: int = 30, epoch: int = 0) -> None:
        self._hmac = HMAC(SHA1(), key)
        self._digits = max(1, min(10, digits))
        self._period = max(1, period)
        self._epoch = epoch

    def __next__(self) -> int:
        t = int((time.time() - self._epoch) / self._period)
        return HOTP.code(self._hmac, t, self._digits)

    def set_seed(self, seed: int) -> None:
        self._epoch = seed
