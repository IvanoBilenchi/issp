import os
from functools import cached_property

from ._comm import Layer, Message
from ._crypto import BlockCipher, Cipher
from ._hash import sha1, sha256
from ._pad import pkcs7_pad, zero_pad
from ._util import blocks, xor


class Verifier(Layer):
    """A security layer that provides message verification."""

    @cached_property
    def code_size(self) -> int:
        """Code size in bytes."""
        try:
            return getattr(self.__class__, "CODE_SIZE")  # noqa: B009
        except AttributeError:
            return len(self.compute_code(b""))

    def compute_code(self, data: bytes) -> bytes:
        """
        Compute the verification code for the given data.

        :param data: The data to compute the verification code for.
        :returns: The computed verification code.
        """
        raise NotImplementedError

    def verify(self, data: bytes, code: bytes) -> bool:
        """
        Verify that the given data matches the expected verification code.

        :param data: The data to verify.
        :param code: The expected verification code.
        :returns: True if the data matches the code, False otherwise.
        """
        return self.compute_code(data) == code

    def encode(self, msg: Message) -> Message:
        msg.body = self.compute_code(msg.body) + msg.body
        return msg

    def decode(self, msg: Message) -> Message:
        code = msg.body[: self.code_size]
        msg.body = msg.body[self.code_size :]
        if not self.verify(msg.body, code):
            err_msg = "Message verification failed"
            raise ValueError(err_msg)
        return msg


class Hash(Verifier):
    """Hash-based message integrity verifier."""

    @property
    def block_size(self) -> int:
        """Block size in bytes."""
        try:
            return getattr(self.__class__, "BLOCK_SIZE")  # noqa: B009
        except AttributeError:
            return self.code_size


class SHA1(Hash):
    """SHA-1 message integrity verifier."""

    CODE_SIZE = 20
    BLOCK_SIZE = 64

    def compute_code(self, data: bytes) -> bytes:
        return sha1(data)


class SHA256(Hash):
    """SHA-256 message integrity verifier."""

    CODE_SIZE = 32
    BLOCK_SIZE = 64

    def compute_code(self, data: bytes) -> bytes:
        return sha256(data)


class CBCMAC(Verifier):
    """CBC-MAC message authenticator."""

    def __init__(self, cipher: BlockCipher) -> None:
        self._cipher = cipher
        super().__init__()

    def compute_code(self, data: bytes) -> bytes:
        data = pkcs7_pad(len(data).to_bytes(4) + data, self._cipher.block_size)
        last = bytes(self._cipher.block_size)
        for block in blocks(data, self._cipher.block_size):
            last = self._cipher.encrypt(xor(last, block))
        return last


class HMAC(Verifier):
    """HMAC message authenticator."""

    @cached_property
    def code_size(self) -> int:
        return self._hash.code_size

    @property
    def key(self) -> bytes:
        return self._key

    @key.setter
    def key(self, value: bytes) -> None:
        if len(value) > self._hash.block_size:
            value = self._hash.compute_code(value)
        if len(value) < self._hash.block_size:
            value = zero_pad(value, self._hash.block_size)
        self._key = value

    def __init__(self, hash_fn: Hash, key: bytes | None = None) -> None:
        self._hash = hash_fn
        self._o_pad_val = b"\x5c" * self._hash.block_size
        self._i_pad_val = b"\x36" * self._hash.block_size
        self.key = key or os.urandom(self._hash.block_size)
        super().__init__()

    def compute_code(self, data: bytes) -> bytes:
        o_pad = xor(self.key, self._o_pad_val)
        i_pad = xor(self.key, self._i_pad_val)
        return self._hash.compute_code(o_pad + self._hash.compute_code(i_pad + data))


class Signature(Verifier):
    """Digital signature verifier."""

    def __init__(self, hash_fn: Hash, cipher: Cipher) -> None:
        self._hash = hash_fn
        self._cipher = cipher
        super().__init__()

    def compute_code(self, data: bytes) -> bytes:
        iv = os.urandom(self._cipher.iv_size) if self._cipher.iv_size else b""
        return iv + self._cipher.encrypt(self._hash.compute_code(data), iv=iv)

    def verify(self, data: bytes, code: bytes) -> bool:
        iv = code[: self._cipher.iv_size] if self._cipher.iv_size else b""
        digest = self._cipher.decrypt(code[self._cipher.iv_size :], iv=iv)
        return self._hash.compute_code(data) == digest
