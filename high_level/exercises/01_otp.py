# Alice and Bob want to exchange messages over an insecure channel. They decide to do so
# using the One-Time Pad (OTP) encryption algorithm. Luckily, they already share a secret key.
#
# Implement the OTP encryption and decryption functions, and use them
# to ensure the confidentiality of messages exchanged between Alice and Bob.

import os

from issp import Actor, Channel, Message, log


def alice(channel: Channel, key: bytes) -> None:
    msg = Message("Alice", "Bob", b"Hello, Bob!")
    log.info("[Alice] Encrypted: %s", msg)
    # TO-DO: encrypt the message body.
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive("Bob")
    # TO-DO: decrypt the message body.
    log.info("[Bob] Decrypted: %s", msg)


def mallory(channel: Channel) -> None:
    channel.peek()


def main() -> None:
    key = os.urandom(16)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    main()
