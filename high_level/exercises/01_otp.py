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


def alice(channel: Channel) -> None:
    msg = Message("Alice", "Bob", b"Hello, Bob!")
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
