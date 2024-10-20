import os
import sys
import time
from abc import ABC, abstractmethod

from ._encryption import AES, BlockCipher
from ._util import byte_size, xor


class RNG[T: (int, bytes)](ABC):
    @abstractmethod
    def next_value(self) -> T:
        pass

    @abstractmethod
    def set_seed(self, seed: T) -> None:
        pass

    def _gen_int(self, first: int, size: int) -> bytes:
        array = bytearray(first.to_bytes(byte_size(first), sys.byteorder))

        while len(array) < size:
            val = self.next_value()
            array.extend(val.to_bytes(byte_size(val), sys.byteorder))

        return bytes(array[:size])

    def _gen_bytes(self, first: bytes, size: int) -> bytes:
        array = bytearray(first)
        while len(array) < size:
            array.extend(self.next_value())
        return bytes(array[:size])

    def generate(self, size: int) -> bytes:
        val = self.next_value()
        return self._gen_int(val, size) if isinstance(val, int) else self._gen_bytes(val, size)


class LCG(RNG[int]):
    def __init__(self, a: int = 16807, c: int = 0, m: int = 2**31 - 1) -> None:
        self._state = time.time_ns() % m
        self._a = a % m
        self._c = c % m
        self._m = m

    def next_value(self) -> int:
        self._state = (self._a * self._state + self._c) % self._m
        return self._state

    def set_seed(self, seed: int) -> None:
        self._state = seed


class CounterRNG(RNG[bytes]):
    def __init__(self, cipher: BlockCipher = None) -> None:
        self._counter = 0
        if cipher is None:
            cipher = AES()
            cipher.apply_padding = False
        self._cipher = cipher

    def next_value(self) -> bytes:
        self._counter += 1
        return self._cipher.encrypt(self._counter.to_bytes(self._cipher.block_size))

    def set_seed(self, seed: bytes) -> None:
        self._cipher.key = seed


class ANSIx917(RNG[bytes]):
    def __init__(self, cipher: BlockCipher = None) -> None:
        if cipher is None:
            cipher = AES()
            cipher.apply_padding = False
        self._cipher = cipher
        self._state = self._cipher.encrypt(os.urandom(self._cipher.block_size))

    def next_value(self) -> bytes:
        temp = self._cipher.encrypt(time.time_ns().to_bytes(self._cipher.block_size))
        output = self._cipher.encrypt(xor(self._state, temp))
        self._state = self._cipher.encrypt(xor(output, temp))
        return output

    def set_seed(self, seed: bytes) -> None:
        self._cipher.key = seed


class TRNG(RNG[bytes]):
    def next_value(self) -> bytes:
        return os.urandom(1)

    def set_seed(self, seed: bytes) -> None:
        del seed  # Unused

    def generate(self, size: int) -> bytes:
        return os.urandom(size)