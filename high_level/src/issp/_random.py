import secrets
import string
from collections.abc import Sequence


def random_bytes(size: int) -> bytes:
    """
    Generate random bytes using the system's secure random number generator.

    :param size: The number of random bytes to generate.
    :return: A bytes object containing random bytes.
    """
    return secrets.token_bytes(size)


def random_string(length: int, charset: str = string.printable) -> str:
    """
    Generate a random string of the specified length using the given character set.

    :param length: The length of the random string.
    :param charset: The character set to use for generating the string.
    :return: A random string.
    """
    return "".join(secrets.choice(charset) for _ in range(length))


def random_int(min_value: int = 0, max_value: int = 2**32 - 1) -> int:
    """
    Generate a random integer within the specified range.

    :param min_value: The minimum value (inclusive).
    :param max_value: The maximum value (inclusive).
    :return: A random integer within the specified range.
    """
    return secrets.randbelow(max_value - min_value + 1) + min_value


def random_choice[T](sequence: Sequence[T]) -> T:
    """
    Select a random element from the given sequence.

    :param sequence: The sequence to choose from.
    :return: A randomly selected element from the sequence.
    """
    return secrets.choice(sequence)
