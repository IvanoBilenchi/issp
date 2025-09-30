# Alice and Bob want to exchange messages over an insecure channel. They decide to do so
# using the One-Time Pad (OTP) encryption algorithm. Luckily, they already share a secret key.
#
# Implement the OTP encryption and decryption functions, and use them
# to ensure the confidentiality of messages exchanged between Alice and Bob.
#
# Hints:
# - Assume that the shared key is held in the global variable KEY,
#   and that it is not available to Mallory.

import os

from issp import Channel, Message, log, start_actors

KEY = os.urandom(16)  # Shared key


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(a[i] ^ b[i] for i in range(len(a)))


def encrypt(data: bytes, key: bytes) -> bytes:
    return xor(data, key)


def decrypt(data: bytes, key: bytes) -> bytes:
    return xor(data, key)


def alice(channel: Channel) -> None:
    msg = Message("Alice", "Bob", b"Hello, Bob!")
    log.info("[Alice] Encrypted: %s", msg)
    msg.body = encrypt(msg.body, KEY)
    channel.send(msg)


def bob(channel: Channel) -> None:
    msg = channel.receive("Bob")
    msg.body = decrypt(msg.body, KEY)
    log.info("[Bob] Decrypted: %s", msg)


def mallory(channel: Channel) -> None:
    channel.peek()


if __name__ == "__main__":
    start_actors(alice, bob, mallory)
