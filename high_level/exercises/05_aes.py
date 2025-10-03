# Ensure the confidentiality of messages exchanged between Alice and Bob by
# implementing AES256 encryption in CBC mode with PKCS7 padding, this time using
# the `cryptography` library.
#
# Hints:
# - Have a look at the cryprography.hazmat.primitives.ciphers module:
#   https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption
# - The library also provides primitives for padding:
#   https://cryptography.io/en/latest/hazmat/primitives/padding

import os

from issp import Actor, Channel, Message, log

BLOCK_SIZE = 16


def encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    # TO-DO: Implement AES256 CBC encryption with PKCS7 padding.
    return data


def decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    # TO-DO: Implement AES256 CBC decryption with PKCS7 unpadding.
    return data


def alice(channel: Channel, key: bytes) -> None:
    msg = Message("Alice", "Bob", b"Here is the top-secret PIN, keep it safe: 42")
    log.info("[Alice] Encrypted: %s", msg)
    # TO-DO: Encrypt the message body.
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive("Bob")
    # TO-DO: Decrypt the message body.
    log.info("[Bob] Decrypted: %s", msg)


def mallory(channel: Channel) -> None:
    channel.peek()


def main() -> None:
    key = os.urandom(32)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    main()
