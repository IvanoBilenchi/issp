from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


def _hmac(data: bytes, key: bytes, algorithm: hashes.HashAlgorithm) -> bytes:
    mac = hmac.HMAC(key, algorithm)
    mac.update(data)
    return mac.finalize()


def _hash(data: bytes, algorithm: hashes.HashAlgorithm, salt: bytes | None = None) -> bytes:
    digest = hashes.Hash(algorithm)
    digest.update(data)
    if salt:
        digest.update(salt)
    return digest.finalize()


def _scrypt(data: bytes, n: int = 2**14, salt: bytes | None = None) -> bytes:
    return Scrypt(salt=b"" if salt is None else salt, length=32, n=n, r=8, p=1).derive(data)


def hmac_sha1(data: bytes, key: bytes) -> bytes:
    """
    HMAC using SHA-1 as the hash function.

    :param data: The data to be authenticated.
    :param key: The secret key (should be 20 bytes long).
    :return: The resulting HMAC.
    """
    return _hmac(data, key, hashes.SHA1())  # noqa: S303


def hmac_sha256(data: bytes, key: bytes) -> bytes:
    """
    HMAC using SHA-256 as the hash function.

    :param data: The data to be authenticated.
    :param key: The secret key (should be 32 bytes long).
    :return: The resulting HMAC.
    """
    return _hmac(data, key, hashes.SHA256())


def sha1(data: bytes, salt: bytes | None = None) -> bytes:
    """
    SHA-1 hash function.

    :param data: The data to be hashed.
    :param salt: Optional salt to be added to the data before hashing.
    :return: The resulting hash.
    """
    return _hash(data, hashes.SHA1(), salt)  # noqa: S303


def sha256(data: bytes, salt: bytes | None = None) -> bytes:
    """
    SHA-256 hash function.

    :param data: The data to be hashed.
    :param salt: Optional salt to be added to the data before hashing.
    :return: The resulting hash.
    """
    return _hash(data, hashes.SHA256(), salt)


def scrypt(data: bytes, salt: bytes | None = None) -> bytes:
    """
    Scrypt hash function.

    :param data: The data to be hashed.
    :param salt: Optional salt to be added to the data before hashing.
    :return: The resulting hash.
    """
    return _scrypt(data, salt=salt)


def scrypt_fast(data: bytes, salt: bytes | None = None) -> bytes:
    """
    Faster, less secure Scrypt hash function.

    :param data: The data to be hashed.
    :param salt: Optional salt to be added to the data before hashing.
    :return: The resulting hash.
    """
    return _scrypt(data, salt=salt, n=2**8)
