from collections.abc import Iterable


def xor(a: Iterable[int], b: Iterable[int]) -> bytes:
    return bytes(a_byte ^ b_byte for (a_byte, b_byte) in zip(a, b, strict=False))


def byte_size(number: int) -> int:
    return (number.bit_length() + 7) // 8


def blocks(data: bytes, block_size: int) -> Iterable[bytes]:
    for i in range(0, len(data), block_size):
        yield data[i : i + block_size]


def snake_to_camel(s: str) -> str:
    return "".join(word.capitalize() for word in s.split("_"))
