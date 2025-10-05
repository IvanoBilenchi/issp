from __future__ import annotations

import os
from typing import TYPE_CHECKING

from cryptography.hazmat.primitives import ciphers
from cryptography.hazmat.primitives.ciphers import algorithms, modes

from ._comm import Layer, Message
from ._pad import pkcs7_pad, pkcs7_unpad
from ._util import blocks, xor

if TYPE_CHECKING:
    from collections.abc import Iterator


class Cipher(Layer):
    """A security layer that encrypts and decrypts messages using a given cipher."""

    @property
    def iv_size(self) -> int:
        """Initialization vector (IV) size in bytes."""
        try:
            return getattr(self.__class__, "IV_SIZE")  # noqa: B009
        except AttributeError:
            raise NotImplementedError from None

    @property
    def key_size(self) -> int:
        """Key size in bytes."""
        try:
            return getattr(self.__class__, "KEY_SIZE")  # noqa: B009
        except AttributeError:
            raise NotImplementedError from None

    def encrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        """
        Encryption function.

        :param data: The plaintext data to encrypt.
        :param iv: The initialization vector (IV) to use for encryption.
        :returns: The encrypted ciphertext.
        """
        raise NotImplementedError

    def decrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        """
        Decryption function.

        :param data: The ciphertext data to decrypt.
        :param iv: The initialization vector (IV) to use for decryption.
        :returns: The decrypted plaintext.
        """
        raise NotImplementedError

    def encode(self, msg: Message) -> Message:
        iv = os.urandom(self.iv_size) if self.iv_size else b""
        data = self.encrypt(msg.body, iv=iv)
        if iv:
            data = iv + data
        msg.body = data
        return msg

    def decode(self, msg: Message) -> Message:
        if self.iv_size:
            iv = msg.body[: self.iv_size]
            data = msg.body[self.iv_size :]
        else:
            iv = b""
            data = msg.body
        msg.body = self.decrypt(data, iv=iv)
        return msg


class SymmetricCipher(Cipher):
    """Base class for symmetric encryption algorithms."""

    @property
    def key(self) -> bytes:
        """Symmetric key."""
        return self._key

    def __init__(self, key: bytes | None = None) -> None:
        super().__init__()
        self._key = key or os.urandom(self.key_size)


class BlockCipher(SymmetricCipher):
    """Base class for block cipher algorithms."""

    @property
    def block_size(self) -> int:
        """Block size in bytes."""
        try:
            return getattr(self.__class__, "BLOCK_SIZE")  # noqa: B009
        except AttributeError:
            raise NotImplementedError from None

    @property
    def iv_size(self) -> int:
        """Initialization vector (IV) size in bytes."""
        return self.block_size


class StreamCipher(SymmetricCipher):
    """Base class for stream cipher algorithms."""

    def key_stream(self, iv: bytes) -> Iterator[int]:
        """
        Keystream generator function.

        :param iv: The initialization vector (IV) to use for keystream generation.
        :yields: A sequence of keystream bytes.
        """
        raise NotImplementedError

    def encrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        return xor(data, self.key_stream(iv))

    def decrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        return xor(data, self.key_stream(iv))


class BlockCipherMode(BlockCipher):
    """Base class for block cipher modes of operation."""

    @property
    def key(self) -> bytes:
        return self._cipher.key

    @property
    def key_size(self) -> int:
        return self._cipher.key_size

    @property
    def block_size(self) -> int:
        return self._cipher.block_size

    def __init__(self, cipher: BlockCipher) -> None:
        self._cipher = cipher
        super().__init__()


class ECB(BlockCipherMode):
    """Electronic Codebook (ECB) mode of operation."""

    def encrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        del iv  # unused
        array = bytearray()
        for block in blocks(pkcs7_pad(data, self.block_size), self.block_size):
            array.extend(self._cipher.encrypt(block))
        return bytes(array)

    def decrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        del iv  # unused
        array = bytearray()
        for block in blocks(data, self.block_size):
            array.extend(self._cipher.decrypt(block))
        return pkcs7_unpad(array, self.block_size)


class CBC(BlockCipherMode):
    """Cipher Block Chaining (CBC) mode of operation."""

    def encrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        array = bytearray()
        last = iv
        for block in blocks(pkcs7_pad(data, self.block_size), self.block_size):
            enc_block = self._cipher.encrypt(xor(last, block))
            array.extend(enc_block)
            last = enc_block
        return bytes(array)

    def decrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        array = bytearray()
        last = iv
        for block in blocks(data, self.block_size):
            array.extend(xor(last, self._cipher.decrypt(block)))
            last = block
        return pkcs7_unpad(array, self.block_size)


class CTR(BlockCipherMode, StreamCipher):
    """Counter (CTR) mode of operation."""

    def key_stream(self, iv: bytes) -> Iterator[int]:
        counter = int.from_bytes(iv)
        while True:
            yield from self._cipher.encrypt(counter.to_bytes(self.block_size))
            counter += 1


class AsymmetricCipher(Cipher):
    """Base class for asymmetric encryption algorithms."""

    @property
    def public_key(self) -> bytes:
        """Public key."""
        raise NotImplementedError

    @property
    def private_key(self) -> bytes:
        """Private key."""
        raise NotImplementedError


class OTP(StreamCipher):
    """One-Time Pad (OTP) cipher with 256 bytes key."""

    KEY_SIZE = 256
    IV_SIZE = 0

    def key_stream(self, iv: bytes) -> Iterator[int]:
        del iv  # unused
        yield from self.key


class AES256(BlockCipher):
    """AES256 cipher."""

    KEY_SIZE = 32
    BLOCK_SIZE = 16

    def encrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        del iv  # unused
        if (data_len := len(data)) != self.block_size:
            msg = f"Data ({data_len} B) must be {self.block_size} B"
            raise ValueError(msg)
        cipher = ciphers.Cipher(algorithms.AES256(self.key), mode=modes.ECB())  # noqa: S305
        return cipher.encryptor().update(data)

    def decrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        del iv  # unused
        if (data_len := len(data)) != self.block_size:
            msg = f"Data ({data_len} B) must be {self.block_size} B"
            raise ValueError(msg)
        cipher = ciphers.Cipher(algorithms.AES256(self.key), mode=modes.ECB())  # noqa: S305
        return cipher.decryptor().update(data)


class ChaCha20(StreamCipher):
    """ChaCha20 cipher."""

    KEY_SIZE = 32
    IV_SIZE = 16

    def key_stream(self, iv: bytes) -> Iterator[int]:
        cipher = ciphers.Cipher(algorithms.ChaCha20(self.key, iv), mode=None)
        buf = b"\x00" * 1024
        while True:
            yield from cipher.encryptor().update(buf)


def aes256_encrypt_block(block: bytes, key: bytes) -> bytes:
    """
    Encrypt a single 16-byte block with AES256.

    :param block: The 16-byte block to encrypt.
    :param key: The 32-byte AES256 key.
    :returns: The encrypted 16-byte block.
    """
    return AES256(key).encrypt(block)


def aes256_decrypt_block(block: bytes, key: bytes) -> bytes:
    """
    Decrypt a single 16-byte block with AES256.

    :param block: The 16-byte block to decrypt.
    :param key: The 32-byte AES256 key.
    :returns: The decrypted 16-byte block.
    """
    return AES256(key).decrypt(block)
