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
    pad = size - len(data) % size
    return data + bytes([pad] * pad)


def pkcs7_unpad(data: bytes, size: int) -> bytes:
    """
    Remove PKCS#7 padding from data.

    :param data: Padded data.
    :param size: Block size in bytes.
    :return: Unpadded data.
    """
    pad = data[-1] if data else 0
    if len(data) % size or not 0 < pad <= size or data[-pad:] != bytes([pad] * pad):
        err_msg = "Invalid padding"
        raise ValueError(err_msg)
    return data[:-pad]


def pkcs1v15_unpad(data: bytes) -> bytes:
    """
    Remove PKCS#1 v1.5 padding from data.

    :param data: Padded data.
    :return: Unpadded data.
    """
    if len(data) < 11 or data[0] != 0x00 or data[1] != 0x02:  # noqa: PLR2004
        err_msg = "Invalid padding"
        raise ValueError(err_msg)
    try:
        sep_index = data.index(0x00, 2)
    except ValueError:
        err_msg = "Invalid padding"
        raise ValueError(err_msg) from None
    return data[sep_index + 1 :]
