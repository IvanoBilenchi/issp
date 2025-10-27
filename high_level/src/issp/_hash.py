from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


def _hash(data: bytes | str, algorithm: hashes.HashAlgorithm, salt: bytes | None = None) -> bytes:
    digest = hashes.Hash(algorithm)
    digest.update(data.encode() if isinstance(data, str) else data)
    if salt:
        digest.update(salt)
    return digest.finalize()


def _scrypt(data: bytes | str, n: int = 2**14, salt: bytes | None = None) -> bytes:
    kdf = Scrypt(salt=b"" if salt is None else salt, length=32, n=n, r=8, p=1)
    return kdf.derive(data.encode() if isinstance(data, str) else data)


def sha1(data: bytes | str, salt: bytes | None = None) -> bytes:
    """
    SHA-1 hash function.

    :param data: The data to be hashed.
    :param salt: Optional salt to be added to the data before hashing.
    :return: The resulting hash.
    """
    return _hash(data, hashes.SHA1(), salt)  # noqa: S303


def sha256(data: bytes | str, salt: bytes | None = None) -> bytes:
    """
    SHA-256 hash function.

    :param data: The data to be hashed.
    :param salt: Optional salt to be added to the data before hashing.
    :return: The resulting hash.
    """
    return _hash(data, hashes.SHA256(), salt)


def scrypt(data: bytes | str, salt: bytes | None = None) -> bytes:
    """
    Scrypt hash function.

    :param data: The data to be hashed.
    :param salt: Optional salt to be added to the data before hashing.
    :return: The resulting hash.
    """
    return _scrypt(data, salt=salt)


def scrypt_fast(data: bytes | str, salt: bytes | None = None) -> bytes:
    """
    Faster, less secure Scrypt hash function.

    :param data: The data to be hashed.
    :param salt: Optional salt to be added to the data before hashing.
    :return: The resulting hash.
    """
    return _scrypt(data, salt=salt, n=2**8)
