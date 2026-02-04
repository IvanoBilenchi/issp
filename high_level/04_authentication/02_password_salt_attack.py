# Mallory managed to obtain the password database of a critical system. The database
# contains user IDs and their corresponding hashed and salted passwords. She knows that many users
# tend to use common passwords, and she has a list of such common passwords.
#
# Your task is to help Mallory crack as many passwords as possible using a dictionary attack.
#
# Hints:
# - You can either precompute all hashed passwords for all salt values, or just
#   compute hashes on-the-fly as needed. Which approach is more efficient, and why?

from itertools import islice

from issp import generate_password_database, log, run_main, scrypt_fast

# Note: We are deliberately using a fast hash function to make the dictionary attack
#       feasible in a reasonable amount of time.
hash_fn = scrypt_fast


def crack_db(db: dict[int, dict[str, bytes]]) -> dict[int, str]:
    cracked: dict[int, str] = {}  # User ID -> plaintext password
    # TO-DO: Crack as many passwords as possible using a dictionary attack.
    return cracked


def main() -> None:
    db = generate_password_database(100, hash_function=hash_fn, salt_length=8)

    log.info("First 10 database entries:")
    for user, data in islice(db.items(), 10):
        log.info("User %d: %s", user, data)

    log.info("Cracking...")
    cracked = crack_db(db)

    log.info("Cracked %d passwords out of %d", len(cracked), len(db))
    log.info("First 10 cracked passwords:")
    for i, password in islice(cracked.items(), 10):
        log.info("%d: %s", i, password)


if __name__ == "__main__":
    run_main(main)
