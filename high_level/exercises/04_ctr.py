# Implement the CTR block cipher mode of operation for AES256 and use it to ensure
# the confidentiality of messages exchanged between Alice and Bob.

import os

from issp import Channel, Message, log, start_actors

KEY = os.urandom(32)
BLOCK_SIZE = 16


def encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    # Implement CTR encryption here.
    return data


def decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    # Implement CTR decryption here.
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
