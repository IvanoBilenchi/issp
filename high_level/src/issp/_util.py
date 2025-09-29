def xor(a: bytes, b: bytes) -> bytes:
    a_size, b_size = len(a), len(b)
    if a_size > b_size:
        err_msg = f"RHS ({b_size} B) is too short for LHS ({a_size} B)"
        raise ValueError(err_msg)
    return bytes(a[i] ^ b[i] for i in range(a_size))


def byte_size(number: int) -> int:
    return (number.bit_length() + 7) // 8


def snake_to_camel(s: str) -> str:
    return "".join(word.capitalize() for word in s.split("_"))
