# Implement the CBC block cipher mode of operation for AES256 and use it to ensure
# the confidentiality of messages exchanged between Alice and Bob.
#
# Hints:
# - You may use the `pkcs7_pad` and `pkcs7_unpad` functions from the `issp` module for
#   a secure and unambiguous padding scheme.

import os

from issp import Actor, Channel, Message, log, run_main

BLOCK_SIZE = 16


def encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    # TO-DO: Implement AES256 CBC encryption.
    return data


def decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    # TO-DO: Implement AES256 CBC decryption.
    return data


def alice(channel: Channel, key: bytes) -> None:
    msg = Message("Alice", "Bob", "Here is the top-secret PIN, keep it safe: 42")
    log.info("[Alice] Encrypted: %s", msg)
    # TO-DO: Generate a random IV, encrypt the message body, and prepend the IV to the ciphertext.
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive("Bob")
    # TO-DO: Extract the IV from the beginning of the message body and decrypt the ciphertext.
    log.info("[Bob] Decrypted: %s", msg)


def mallory(channel: Channel) -> None:
    channel.peek()


def main() -> None:
    key = os.urandom(32)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    run_main(main)
