from __future__ import annotations

import os
from abc import ABC, abstractmethod

from cryptography.hazmat.primitives import ciphers, padding
from cryptography.hazmat.primitives.ciphers import algorithms, modes

from ._communication import Layer, Message
from ._util import xor


class EncryptionLayer(Layer):
    def __init__(self, cipher: Cipher) -> None:
        super().__init__()
        self._cipher = cipher

    def write(self, msg: Message) -> None:
        iv = os.urandom(self._cipher.iv_size) if self._cipher.iv_size else b""
        data = self._cipher.encrypt(msg.body, iv=iv)
        if iv:
            data = iv + data
        msg.body = data
        super().write(msg)

    def read(self) -> Message:
        msg = super().read()
        if self._cipher.iv_size:
            iv = msg.body[: self._cipher.iv_size]
            data = msg.body[self._cipher.iv_size :]
        else:
            iv = b""
            data = msg.body
        msg.body = self._cipher.decrypt(data, iv=iv)
        return msg


class Cipher(ABC):
    @property
    def iv_size(self) -> int:
        try:
            return getattr(self.__class__, "IV_SIZE")  # noqa: B009
        except AttributeError:
            raise NotImplementedError from None

    @property
    def key_size(self) -> int:
        try:
            return getattr(self.__class__, "KEY_SIZE")  # noqa: B009
        except AttributeError:
            raise NotImplementedError from None

    @abstractmethod
    def encrypt(self, data: bytes, *, iv: bytes) -> bytes:
        return data

    @abstractmethod
    def decrypt(self, data: bytes, *, iv: bytes) -> bytes:
        return data


class SymmetricCipher(Cipher, ABC):
    def __init__(self, key: bytes | None = None) -> None:
        super().__init__()
        self.key = key or os.urandom(self.key_size)


class BlockCipher(SymmetricCipher, ABC):
    @property
    def block_size(self) -> int:
        try:
            return getattr(self.__class__, "BLOCK_SIZE")  # noqa: B009
        except AttributeError:
            raise NotImplementedError from None

    @property
    def iv_size(self) -> int:
        return self.block_size


class AsymmetricCipher(Cipher, ABC):
    @property
    @abstractmethod
    def public_key(self) -> bytes:
        pass

    @property
    @abstractmethod
    def private_key(self) -> bytes:
        pass


class OTP(SymmetricCipher):
    KEY_SIZE = 256
    IV_SIZE = 0

    def encrypt(self, data: bytes, *, iv: bytes) -> bytes:
        del iv  # unused
        return xor(data, self.key)

    def decrypt(self, data: bytes, *, iv: bytes) -> bytes:
        del iv  # unused
        return xor(data, self.key)


class AES256(BlockCipher):
    KEY_SIZE = 32
    BLOCK_SIZE = 16

    def __init__(self, key: bytes | None = None) -> None:
        super().__init__(key)
        self._pad = padding.PKCS7(self.block_size * 8)
        self.apply_padding = True

    def encrypt(self, data: bytes, *, iv: bytes) -> bytes:
        encryptor = ciphers.Cipher(algorithms.AES(self.key), modes.CBC(iv)).encryptor()
        if self.apply_padding:
            padder = self._pad.padder()
            data = padder.update(data) + padder.finalize()
        return encryptor.update(data) + encryptor.finalize()

    def decrypt(self, data: bytes, *, iv: bytes) -> bytes:
        decryptor = ciphers.Cipher(algorithms.AES(self.key), modes.CBC(iv)).decryptor()
        data = decryptor.update(data) + decryptor.finalize()
        if self.apply_padding:
            unpadder = self._pad.unpadder()
            data = unpadder.update(data) + unpadder.finalize()
        return data


class ChaCha20(SymmetricCipher):
    KEY_SIZE = 32
    IV_SIZE = 16

    def encrypt(self, data: bytes, *, iv: bytes) -> bytes:
        cipher = ciphers.Cipher(algorithms.ChaCha20(self.key, iv), mode=None)
        return cipher.encryptor().update(data)

    def decrypt(self, data: bytes, *, iv: bytes) -> bytes:
        cipher = ciphers.Cipher(algorithms.ChaCha20(self.key, iv), mode=None)
        return cipher.decryptor().update(data)


def aes256_encrypt_block(block: bytes, key: bytes) -> bytes:
    if len(block) != (expected := AES256.BLOCK_SIZE):
        msg = f"Block size must be {expected} bytes"
        raise ValueError(msg)
    cipher = ciphers.Cipher(algorithms.AES256(key), mode=modes.ECB())  # noqa: S305
    return cipher.encryptor().update(block)


def aes256_decrypt_block(block: bytes, key: bytes) -> bytes:
    if len(block) != (expected := AES256.BLOCK_SIZE):
        msg = f"Block size must be {expected} bytes"
        raise ValueError(msg)
    cipher = ciphers.Cipher(algorithms.AES256(key), mode=modes.ECB())  # noqa: S305
    return cipher.decryptor().update(block)
