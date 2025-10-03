# Implement the ECB block cipher mode of operation for AES256 and use it to ensure
# the confidentiality of messages exchanged between Alice and Bob.
#
# Hints:
# - Use the `aes256_encrypt_block` and `aes256_decrypt_block` functions from the `issp` module.
# - Remember that we are dealing with a block cipher, so you might need to add padding
#   to the plaintext to make its length a multiple of the block size. For simplicity,
#   you can use zero padding (i.e., append zero bytes to the plaintext), though be aware
#   that this is not a secure padding scheme and it does not account for the case where
#   the plaintext actually ends with zero bytes.

import os

from issp import Actor, Channel, Message, aes256_decrypt_block, aes256_encrypt_block, log

BLOCK_SIZE = 16  # AES256 block size in bytes


def zero_pad(data: bytes, block_size: int) -> bytes:
    if remainder := len(data) % block_size:
        data += bytes(block_size - remainder)
    return data


def zero_unpad(data: bytes) -> bytes:
    return data.rstrip(b"\x00")


def encrypt(data: bytes, key: bytes) -> bytes:
    array = bytearray()
    for i in range(0, len(data), BLOCK_SIZE):
        block = data[i : i + BLOCK_SIZE]
        array.extend(aes256_encrypt_block(block, key))
    return bytes(array)


def decrypt(data: bytes, key: bytes) -> bytes:
    array = bytearray()
    for i in range(0, len(data), BLOCK_SIZE):
        block = data[i : i + BLOCK_SIZE]
        array.extend(aes256_decrypt_block(block, key))
    return bytes(array)


def alice(channel: Channel, key: bytes) -> None:
    msg = Message("Alice", "Bob", b"Here is the top-secret PIN, keep it safe: 42")
    log.info("[Alice] Encrypted: %s", msg)
    msg.body = encrypt(zero_pad(msg.body, BLOCK_SIZE), key)
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive("Bob")
    msg.body = zero_unpad(decrypt(msg.body, key))
    log.info("[Bob] Decrypted: %s", msg)


def mallory(channel: Channel) -> None:
    channel.peek()


def main() -> None:
    key = os.urandom(32)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    main()
