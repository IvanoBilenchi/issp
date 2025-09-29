from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

AES256_BLOCK_SIZE = 16


def aes256_encrypt_block(block: bytes, key: bytes) -> bytes:
    if len(block) != AES256_BLOCK_SIZE:
        msg = f"Block size must be {AES256_BLOCK_SIZE} bytes"
        raise ValueError(msg)
    return Cipher(algorithms.AES256(key), modes.ECB()).encryptor().update(block)  # noqa: S305


def aes256_decrypt_block(block: bytes, key: bytes) -> bytes:
    if len(block) != AES256_BLOCK_SIZE:
        msg = f"Block size must be {AES256_BLOCK_SIZE} bytes"
        raise ValueError(msg)
    return Cipher(algorithms.AES256(key), modes.ECB()).decryptor().update(block)  # noqa: S305
