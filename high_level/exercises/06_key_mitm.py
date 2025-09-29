# Alice and Bob want to exchange messages over an insecure channel. They decide to do so
# using the One-Time Pad (OTP) encryption algorithm. However, they do not share a secret key,
# so they must first exchange it over an insecure channel. Mallory is listening.
#
# Allow Mallory to:
# 1. Eavesdrop on the communication between Alice and Bob.
# 2. Tamper with the message sent by Alice to Bob.

import os

from issp import Channel, Message, log, start_actors, xor


def encrypt(data: bytes, key: bytes) -> bytes:
    return xor(data, key)


def decrypt(data: bytes, key: bytes) -> bytes:
    return xor(data, key)


def alice(channel: Channel) -> None:
    key = os.urandom(16)

    channel.send(Message("Alice", "Bob", key))
    channel.receive("Alice")

    msg = Message("Alice", "Bob", b"Hello, Bob!")
    log.info("[Alice] Encrypted: %s", msg)
    msg.body = encrypt(msg.body, key)
    channel.send(msg)


def bob(channel: Channel) -> None:
    msg = channel.receive("Bob")
    key = msg.body
    channel.send(Message("Bob", "Alice", b"Key received"))

    msg = channel.receive("Bob")
    msg.body = decrypt(msg.body, key)
    log.info("[Bob] Decrypted: %s", msg)


def mallory(channel: Channel) -> None:
    # Delete this code and implement eavesdropping and tampering.
    for _ in range(3):
        channel.peek()
        channel.wait()


if __name__ == "__main__":
    start_actors(alice, bob, mallory)
