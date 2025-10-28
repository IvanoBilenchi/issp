# Alice and Bob want to exchange messages over an insecure channel. They decide to do so
# using the One-Time Pad (OTP) encryption algorithm. However, they do not share a secret key,
# so they must first exchange it. Mallory is listening.
#
# Allow Mallory to:
# 1. Eavesdrop on the communication between Alice and Bob.
# 2. Tamper with the message sent by Alice to Bob.

import os

from issp import Actor, Channel, Message, log, run_main, xor


def encrypt(data: bytes, key: bytes) -> bytes:
    return xor(data, key)


def decrypt(data: bytes, key: bytes) -> bytes:
    return xor(data, key)


def alice(channel: Channel) -> None:
    key = os.urandom(16)
    channel.send(Message("Alice", "Bob", key))

    msg = Message("Alice", "Bob", "Hello, Bob!")
    log.info("[Alice] Encrypted: %s", msg)
    msg.body = xor(msg.body, key)
    channel.send(msg)


def bob(channel: Channel) -> None:
    msg = channel.receive("Bob")
    key = msg.body

    msg = channel.receive("Bob")
    msg.body = decrypt(msg.body, key)
    log.info("[Bob] Decrypted: %s", msg)


def mallory(channel: Channel) -> None:
    msg = channel.peek()
    key = msg.body
    channel.wait()

    msg = channel.receive()
    msg.body = decrypt(msg.body, key)
    log.info("[Mallory] Decrypted: %s", msg)

    msg.body = "Screw you, Bob!"
    log.info("[Mallory] Encrypted: %s", msg)
    msg.body = encrypt(msg.body, key)
    channel.send(msg)


def main() -> None:
    Actor.start(Actor(alice), Actor(bob), Actor(mallory, priority=1))


if __name__ == "__main__":
    run_main(main)
