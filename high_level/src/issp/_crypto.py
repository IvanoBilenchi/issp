from __future__ import annotations

import math
import os
from typing import TYPE_CHECKING

from cryptography.hazmat.primitives import ciphers, serialization
from cryptography.hazmat.primitives.asymmetric import (
    padding as asymmetric_padding,
    rsa,
)
from cryptography.hazmat.primitives.ciphers import algorithms, modes

from ._bytes import blocks, split, xor
from ._comm import Layer, Message
from ._pad import pkcs1v15_unpad, pkcs7_pad, pkcs7_unpad

if TYPE_CHECKING:
    from collections.abc import Iterator


class Cipher(Layer):
    """A security layer that encrypts and decrypts messages using a given cipher."""

    @property
    def iv_size(self) -> int:
        """Initialization vector (IV) size in bytes."""
        return getattr(self.__class__, "IV_SIZE", 0)

    @property
    def key_size(self) -> int:
        """Key size in bytes."""
        if (size := getattr(self, "KEY_SIZE", 0)) != 0:
            return size
        raise NotImplementedError

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

    def ciphertext_size(self, plaintext: int | bytes) -> int:
        """
        Calculate the size of the ciphertext for a given plaintext size.

        :param plaintext: The size of the plaintext in bytes or the plaintext itself.
        :returns: The size of the ciphertext in bytes.
        """
        plaintext = b"\x00" * plaintext if isinstance(plaintext, int) else plaintext
        iv = b"x\00" * self.iv_size if self.iv_size else b""
        return len(self.encrypt(plaintext, iv=iv))

    def generate_iv(self) -> bytes:
        """Generate a random initialization vector (IV)."""
        return os.urandom(self.iv_size) if self.iv_size else b""

    def encode(self, msg: Message) -> Message:
        iv = self.generate_iv()
        msg.body = iv + self.encrypt(msg.body, iv=iv)
        return msg

    def decode(self, msg: Message) -> Message:
        iv, body = split(msg.body, self.iv_size)
        msg.body = self.decrypt(body, iv=iv)
        return msg


class SymmetricCipher(Cipher):
    """Base class for symmetric encryption algorithms."""

    @property
    def key(self) -> bytes:
        """Symmetric key."""
        raise NotImplementedError

    @key.setter
    def key(self, value: bytes) -> None:
        raise NotImplementedError

    def generate_key(self) -> bytes:
        """Generate a random symmetric key."""
        return os.urandom(self.key_size)


class BaseSymmetricCipher(SymmetricCipher):
    @property
    def key(self) -> bytes:
        return self._key

    @key.setter
    def key(self, value: bytes) -> None:
        self._key = bytes(value)

    def __init__(self, key: bytes | None = None) -> None:
        super().__init__()
        if key and (size := getattr(self, "KEY_SIZE", 0)) != 0 and len(key) != size:
            msg = f"Key must be {size} B, got {len(key)} B"
            raise ValueError(msg)
        self._key = bytes(key) if key else self.generate_key()


class BlockCipher(SymmetricCipher):
    """Base class for block cipher algorithms."""

    @property
    def block_size(self) -> int:
        """Block size in bytes."""
        if (size := getattr(self, "BLOCK_SIZE", 0)) != 0:
            return size
        raise NotImplementedError

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


class BlockCipherMode(Cipher):
    """Base class for block cipher modes of operation."""

    @property
    def key(self) -> bytes:
        return self._cipher.key

    @key.setter
    def key(self, value: bytes) -> None:
        self._cipher.key = value

    @property
    def key_size(self) -> int:
        return self._cipher.key_size

    @property
    def block_size(self) -> int:
        return self._cipher.block_size

    def __init__(self, cipher: BlockCipher) -> None:
        super().__init__()
        self._cipher = cipher

    def generate_key(self) -> bytes:
        return self._cipher.generate_key()

    def generate_iv(self) -> bytes:
        return self._cipher.generate_iv()


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
            last = self._cipher.encrypt(xor(last, block))
            array.extend(last)
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


class OTP(BaseSymmetricCipher, StreamCipher):
    """One-Time Pad (OTP) cipher with 256 bytes key."""

    KEY_SIZE = 256

    def key_stream(self, iv: bytes) -> Iterator[int]:
        del iv  # unused
        yield from self.key


class AES256(BaseSymmetricCipher, BlockCipher):
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


class ChaCha20(BaseSymmetricCipher, StreamCipher):
    """ChaCha20 cipher."""

    KEY_SIZE = 32
    IV_SIZE = 16

    def key_stream(self, iv: bytes) -> Iterator[int]:
        cipher = ciphers.Cipher(algorithms.ChaCha20(self.key, iv), mode=None)
        buf = b"\x00" * 1024
        while True:
            yield from cipher.encryptor().update(buf)


class AsymmetricKey(Cipher):
    """Base class for asymmetric keys."""

    @property
    def key_bytes(self) -> bytes:
        """Key bytes."""
        raise NotImplementedError


class AsymmetricCipher(Cipher):
    """Base class for asymmetric encryption algorithms."""

    @property
    def key_size(self) -> int:
        if self.encryption_key:
            return self.encryption_key.key_size
        if self.decryption_key:
            return self.decryption_key.key_size
        err_msg = "No key available"
        raise ValueError(err_msg)

    @property
    def encryption_key(self) -> AsymmetricKey | None:
        """The encryption key."""
        raise NotImplementedError

    @property
    def decryption_key(self) -> AsymmetricKey | None:
        """The decryption key."""
        raise NotImplementedError

    def encrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        del iv  # unused
        if key := self.encryption_key:
            return key.encrypt(data)
        err_msg = "Encryption key missing"
        raise AttributeError(err_msg)

    def decrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        del iv  # unused
        if key := self.decryption_key:
            return key.decrypt(data)
        err_msg = "Decryption key missing"
        raise AttributeError(err_msg)

    def ciphertext_size(self, plaintext: int | bytes) -> int:
        if self.encryption_key:
            return self.encryption_key.ciphertext_size(plaintext)
        if self.decryption_key:
            return self.decryption_key.ciphertext_size(plaintext)
        err_msg = "No key available"
        raise AttributeError(err_msg)


class RSAKey(AsymmetricKey):
    """Base class for RSA keys."""

    # Note: PKCS1v15 supports the hacks that are needed to force the cryptography
    # library to "encrypt" using private keys and "decrypt" using public keys.
    # In real-world applications, you should use OAEP for encryption and PSS for signing.
    _padding = asymmetric_padding.PKCS1v15()


class RSAPublicKey(RSAKey):
    """RSA public key."""

    @property
    def key_size(self) -> int:
        return self._key.key_size // 8

    @property
    def key_bytes(self) -> bytes:
        return self._key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def __init__(self, key: rsa.RSAPrivateKey | rsa.RSAPublicKey) -> None:
        super().__init__()
        if isinstance(key, rsa.RSAPrivateKey):
            self._key = key.public_key()
            self._dec_key = self._pri_swap_exp(key)
        else:
            self._key = key
            self._dec_key = None

    def encrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        del iv  # unused
        return self._key.encrypt(data, self._padding)

    def decrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        del iv  # unused
        if self._dec_key:
            return self._dec_key.decrypt(data, self._padding)
        # Resort to manual decryption / unpadding.
        e = self._key.public_numbers().e
        n = self._key.public_numbers().n
        key_len = math.ceil(n.bit_length() / 8)
        padded_data = pow(int.from_bytes(data), e, n).to_bytes(key_len)
        return pkcs1v15_unpad(padded_data)

    @staticmethod
    def _pri_swap_exp(key: rsa.RSAPrivateKey) -> rsa.RSAPrivateKey:
        # Returns a RSAPrivateKey by swapping the private exponent d with the public exponent e.
        # This hack is needed to "decrypt" with the public key when in sign_mode.
        pri = key.private_numbers()
        pub = pri.public_numbers
        n_pub = rsa.RSAPublicNumbers(pri.d, pub.n)
        n_pri = rsa.RSAPrivateNumbers(
            pri.p,
            pri.q,
            pub.e,
            rsa.rsa_crt_dmp1(pub.e, pri.p),
            rsa.rsa_crt_dmq1(pub.e, pri.q),
            pri.iqmp,
            n_pub,
        )
        return n_pri.private_key()


class RSAPrivateKey(RSAKey):
    """RSA private key."""

    @property
    def key_size(self) -> int:
        return self._key.key_size // 8

    @property
    def key_bytes(self) -> bytes:
        return self._key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        )

    def __init__(self, key: rsa.RSAPrivateKey) -> None:
        super().__init__()
        self._key = key
        self._enc_key = self._pub_swap_exp(self._key)

    def encrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        del iv  # unused
        return self._enc_key.encrypt(data, self._padding)

    def decrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        del iv  # unused
        return self._key.decrypt(data, self._padding)

    @staticmethod
    def _pub_swap_exp(key: rsa.RSAPrivateKey) -> rsa.RSAPublicKey:
        # Returns a RSAPublicKey by swapping the public exponent e with the private exponent d.
        # This hack is needed to "encrypt" with the private key when in sign_mode.
        n = key.private_numbers()
        return rsa.RSAPublicNumbers(n.d, n.public_numbers.n).public_key()


class RSA(AsymmetricCipher):
    """RSA cipher."""

    @classmethod
    def generate_key_pair(cls, key_size: int = 256) -> tuple[RSAPrivateKey, RSAPublicKey]:
        """
        Generate a new RSA key pair.

        :param key_size: Key size in bytes.
        :returns: A tuple containing the RSA private key and public key.
        """
        pri = rsa.generate_private_key(public_exponent=65537, key_size=key_size * 8)
        return RSAPrivateKey(pri), RSAPublicKey(pri)

    @classmethod
    def load_private_key(cls, data: bytes) -> tuple[RSAPrivateKey, RSAPublicKey]:
        key = serialization.load_pem_private_key(data, password=None)
        if not isinstance(key, rsa.RSAPrivateKey):
            err_msg = "The provided key is not an RSA private key"
            raise TypeError(err_msg)
        return RSAPrivateKey(key), RSAPublicKey(key)

    @classmethod
    def load_public_key(cls, data: bytes) -> RSAPublicKey:
        key = serialization.load_pem_public_key(data)
        if not isinstance(key, rsa.RSAPublicKey):
            err_msg = "The provided public key is not an RSA public key"
            raise TypeError(err_msg)
        return RSAPublicKey(key)

    def __init__(self, encryption_key: RSAKey | None, decryption_key: RSAKey | None) -> None:
        super().__init__()
        self._enc_key = encryption_key
        self._dec_key = decryption_key


class Envelope(Cipher):
    """Digital envelope layer that combines asymmetric and symmetric encryption."""

    @property
    def key_size(self) -> int:
        return self._asym.key_size

    @property
    def iv_size(self) -> int:
        return self._sym.iv_size

    def __init__(self, asym_cipher: AsymmetricCipher, sym_cipher: SymmetricCipher) -> None:
        super().__init__()
        self._asym = asym_cipher
        self._sym = sym_cipher

    def encrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        key = self._sym.generate_key()
        self._sym.key = key
        return self._asym.encrypt(key + iv) + self._sym.encrypt(data, iv=iv)

    def decrypt(self, data: bytes, *, iv: bytes = b"") -> bytes:
        enc_key, enc_msg = split(data, self._asym.key_size)
        key, iv = split(self._asym.decrypt(enc_key), self._sym.key_size)
        self._sym.key = key
        return self._sym.decrypt(enc_msg, iv=iv)


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
