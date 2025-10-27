import os
import random
import string
from collections.abc import Callable
from functools import cache

from . import _log as log
from ._config import RES_DIR
from ._hash import scrypt
from ._rng import random_choice, random_int, random_string


@cache
def common_passwords() -> list[str]:
    """
    Load and return a list of common passwords.

    :return: A list of common passwords.
    """
    with (RES_DIR / "10-million-password-list-top-10000.txt").open() as f:
        return f.read().splitlines()


def random_common_password(length: int = 5, charset: str = string.ascii_lowercase) -> str:
    """
    Select a random common password of the specified length and character set.

    :param length: The length of the password.
    :param charset: The character set to filter passwords.
    :return: A random common password.
    """
    pwds = [p for p in common_passwords() if len(p) == length and all(c in charset for c in p)]
    if not pwds:
        err_msg = "No suitable password found"
        raise ValueError(err_msg)
    return random_choice(pwds)


def generate_password_database(
    length: int,
    random_ratio: float = 0.5,
    random_min_length: int = 8,
    random_max_length: int = 16,
    hash_function: Callable[[bytes, bytes | None], bytes] | None = scrypt,
    salt_length: int = 16,
) -> dict[int, dict[str, bytes]]:
    """
    Generate a password database with a mix of random and common passwords.

    :param length: Total number of passwords to generate.
    :param random_ratio: Ratio of random passwords to total passwords.
    :param random_min_length: Minimum length of random passwords.
    :param random_max_length: Maximum length of random passwords.
    :param hash_function: Hash function to use for password hashing.
    :param salt_length: Length of the salt to use for hashing.
    :return: A dictionary mapping user IDs to password data.
    """
    common = common_passwords()
    repeat_common = length // len(common) + 1
    random_count = int(length * random_ratio)
    common_count = length - random_count

    charset = string.ascii_letters + string.digits
    passwords = [
        random_string(random_int(random_min_length, random_max_length), charset=charset)
        for _ in range(random_count)
    ]
    passwords.extend(random.sample(common, counts=[repeat_common] * len(common), k=common_count))
    random.shuffle(passwords)

    pass_dict: dict[int, dict[str, bytes]] = {
        i: {"password": password.encode()} for i, password in enumerate(passwords)
    }

    if hash_function is not None:
        log.info("Generating password database...")
        for data in log.percent(pass_dict.values()):
            if salt_length > 0:
                salt = os.urandom(16)
                data["salt"] = salt
            else:
                salt = None
            data["password"] = hash_function(data["password"], salt)

    return pass_dict
