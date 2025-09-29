from cryptography.hazmat.primitives import padding


def zero_pad(data: bytes, size: int) -> bytes:
    padding = size - len(data) % size
    return data + bytes(padding) if padding else data


def zero_unpad(data: bytes) -> bytes:
    return data.rstrip(b"\x00")


def pkcs7_pad(data: bytes, size: int) -> bytes:
    padder = padding.PKCS7(size * 8).padder()
    return padder.update(data) + padder.finalize()


def pkcs7_unpad(data: bytes, size: int) -> bytes:
    unpadder = padding.PKCS7(size * 8).unpadder()
    return unpadder.update(data) + unpadder.finalize()
