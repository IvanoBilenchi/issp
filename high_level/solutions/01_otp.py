# Alice and Bob want to exchange messages over an insecure channel. They decide to do so
# using the One-Time Pad (OTP) encryption algorithm. Luckily, they already share a secret key.
#
# Implement the OTP encryption and decryption functions, and use them
# to ensure the confidentiality of messages exchanged between Alice and Bob.

import os

from issp import Actor, Channel, Message, log, run_main


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(a[i] ^ b[i] for i in range(len(a)))


def encrypt(data: bytes, key: bytes) -> bytes:
    return xor(data, key)


def decrypt(data: bytes, key: bytes) -> bytes:
    return xor(data, key)


def alice(channel: Channel, key: bytes) -> None:
    msg = Message("Alice", "Bob", "Hello, Bob!")
    log.info("[Alice] Encrypted: %s", msg)
    msg.body = encrypt(msg.body, key)
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive("Bob")
    msg.body = decrypt(msg.body, key)
    log.info("[Bob] Decrypted: %s", msg)


def mallory(channel: Channel) -> None:
    channel.peek()


def main() -> None:
    key = os.urandom(16)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    run_main(main)
