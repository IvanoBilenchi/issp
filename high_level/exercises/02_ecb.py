# Implement the ECB block cipher mode of operation for AES256 and use it to ensure
# the confidentiality of messages exchanged between Alice and Bob.
#
# Hints:
# - Use the `aes256_encrypt_block` and `aes256_decrypt_block` functions from the `issp` module.
# - You may find the `bytearray` class useful to build the ciphertext/plaintext incrementally.
# - Remember that we are dealing with a block cipher, so you might need to add padding
#   to the plaintext to make its length a multiple of the block size. For simplicity,
#   you can use zero padding (i.e., append zero bytes to the plaintext), though be aware
#   that this is not a secure padding scheme and it does not account for the case where
#   the plaintext actually ends with zero bytes.

import os

from issp import Channel, Message, log, start_actors

KEY = os.urandom(32)  # AES256 shared key
BLOCK_SIZE = 16  # AES256 block size in bytes


def zero_pad(data: bytes, block_size: int) -> bytes:
    # Implement zero padding here.
    return data


def zero_unpad(data: bytes) -> bytes:
    # Implement zero unpadding here.
    return data


def encrypt(data: bytes, key: bytes) -> bytes:
    # Implement ECB encryption here.
    return data


def decrypt(data: bytes, key: bytes) -> bytes:
    # Implement ECB decryption here.
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
