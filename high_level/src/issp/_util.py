import itertools
from collections.abc import Iterable


def xor(a: Iterable[int], b: Iterable[int]) -> bytes:
    """
    XOR two byte sequences.

    If the sequences are of different lengths, the longer one is truncated.

    :param a: First byte sequence.
    :param b: Second byte sequence.
    :return: XOR of the two byte sequences.
    """
    return bytes(a_byte ^ b_byte for (a_byte, b_byte) in zip(a, b, strict=False))


def byte_size(number: int) -> int:
    """
    Return the number of bytes required to represent an integer.

    :param number: The integer to evaluate.
    :return: Number of bytes required to represent the integer.
    """
    return (number.bit_length() + 7) // 8


def blocks(data: bytes, block_size: int) -> Iterable[bytes]:
    """
    Yield successive blocks of data of a given size.

    The last block may be shorter than the specified size.

    :param data: The data to split into blocks.
    :param block_size: The size of each block.
    :return: An iterable of byte blocks.
    """
    for i in range(0, len(data), block_size):
        yield data[i : i + block_size]


def generate_bytes(
    length: int | Iterable[int] = 1,
    alphabet: Iterable[int] | str | None = None,
) -> Iterable[bytes]:
    """
    Generate all possible byte sequences of a given length using symbols from a given alphabet.

    :param length: Length or lengths of the byte sequences to generate.
    :param alphabet: Alphabet of bytes to use. If None, all 256 byte values are used.
                     If a string is provided, its UTF-8 byte values are used.
    :return: An iterable of byte sequences.
    """
    if isinstance(length, int):
        length = (length,)
    if alphabet is None:
        alphabet = range(256)
    elif isinstance(alphabet, str):
        alphabet = alphabet.encode()
    yield from (bytes(k) for l in length for k in itertools.product(alphabet, repeat=l))


def snake_to_camel(s: str) -> str:
    return "".join(word.capitalize() for word in s.split("_"))
