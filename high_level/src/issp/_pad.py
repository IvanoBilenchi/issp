from cryptography.hazmat.primitives import padding


def zero_pad(data: bytes, size: int) -> bytes:
    """
    Pad data with zero bytes to a multiple of the given size.

    :param data: Data to pad.
    :param size: Block size in bytes.
    :return: Padded data.
    """
    padding = size - len(data) % size
    return data + bytes(padding) if padding else data


def zero_unpad(data: bytes) -> bytes:
    """
    Remove zero byte padding from data.

    :param data: Padded data.
    :return: Unpadded data.
    """
    return data.rstrip(b"\x00")


def pkcs7_pad(data: bytes, size: int) -> bytes:
    """
    Pad data using PKCS#7 to a multiple of the given size.

    :param data: Data to pad.
    :param size: Block size in bytes.
    :return: Padded data.
    """
    padder = padding.PKCS7(size * 8).padder()
    return padder.update(data) + padder.finalize()


def pkcs7_unpad(data: bytes, size: int) -> bytes:
    """
    Remove PKCS#7 padding from data.

    :param data: Padded data.
    :param size: Block size in bytes.
    :return: Unpadded data.
    """
    unpadder = padding.PKCS7(size * 8).unpadder()
    return unpadder.update(data) + unpadder.finalize()
