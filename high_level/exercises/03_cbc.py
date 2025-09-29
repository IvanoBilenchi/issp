# Implement the CBC block cipher mode of operation for AES256 and use it to ensure
# the confidentiality of messages exchanged between Alice and Bob.
#
# Hints:
# - CBC requires a random initialization vector for the first block. Make sure
#   to send it along with the ciphertext to Bob, as he will need it for decryption.
# - You may use the `pkcs7_pad` and `pkcs7_unpad` functions from the `issp` module for
#   a secure and unambiguous padding scheme.

import os

from issp import Channel, Message, log, start_actors

KEY = os.urandom(32)
BLOCK_SIZE = 16


def encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    # Implement CBC encryption here.
    return data


def decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    # Implement CBC decryption here.
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
