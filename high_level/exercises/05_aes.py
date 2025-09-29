# Ensure the confidentiality of messages exchanged between Alice and Bob by
# implementing AES256 encryption in CBC mode with PKCS7 padding, this time using
# the `cryptography` library.
#
# Hints:
# - Have a look at the cryprography.hazmat.primitives.ciphers module:
#   https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption

import os

from issp import Channel, Message, log, start_actors

KEY = os.urandom(32)
BLOCK_SIZE = 16


def encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    # Implement AES256 CBC encryption with PKCS7 padding here.
    return data


def decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    # Implement AES256 CBC decryption with PKCS7 unpadding here.
    return data


def alice(channel: Channel) -> None:
    msg = Message("Alice", "Bob", b"Here is the top-secret PIN, keep it safe: 42")
    log.info("[Alice] Encrypted: %s", msg)
    # Encrypt the message body here.
    channel.send(msg)


def bob(channel: Channel) -> None:
    msg = channel.receive("Bob")
    # Decrypt the message body here.
    log.info("[Bob] Decrypted: %s", msg)


def mallory(channel: Channel) -> None:
    channel.peek()


if __name__ == "__main__":
    start_actors(alice, bob, mallory)
