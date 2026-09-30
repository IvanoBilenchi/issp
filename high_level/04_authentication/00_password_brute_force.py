# Mallory wants to gain unauthorized access to a system by cracking the administrator's password.
# She manages to obtain the hashed password. Luckily for her, it has been hashed using a fast
# hash function, and it is known to consist only of lowercase letters.
#
# Your task is to crack the password using a brute-force attack.
#
# Hints:
# - Use the `generate_bytes` function from `issp` to generate candidate passwords.

import string

from issp import log, random_common_password, run_main, sha256

# Note: Try changing the hash function to `scrypt`. Is the attack still feasible?
hash_fn = sha256
CHARSET = string.ascii_lowercase


def crack_password(target: bytes) -> str:
    # TO-DO: Find the password through brute-force.
    err_msg = "Password not found"
    raise ValueError(err_msg)


def main() -> None:
    password = random_common_password(length=5, charset=CHARSET)
    log.info("Password to crack: %s", password)
    password = hash_fn(password.encode())
    log.info("Cracking...")
    found = crack_password(password)
    log.info("Password found: %s", found)


if __name__ == "__main__":
    run_main(main)
