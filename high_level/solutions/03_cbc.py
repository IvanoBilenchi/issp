# Implement the CBC block cipher mode of operation for AES256 and use it to ensure
# the confidentiality of messages exchanged between Alice and Bob.
#
# Hints:
# - You may use the `pkcs7_pad` and `pkcs7_unpad` functions from the `issp` module for
#   a secure and unambiguous padding scheme.

import os

from issp import (
    Actor,
    Channel,
    Message,
    aes256_decrypt_block,
    aes256_encrypt_block,
    log,
    pkcs7_pad,
    pkcs7_unpad,
    xor,
)

BLOCK_SIZE = 16


def encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    array = bytearray()
    last_block = iv
    for i in range(0, len(data), BLOCK_SIZE):
        block = data[i : i + BLOCK_SIZE]
        block = xor(last_block, block)
        block = aes256_encrypt_block(block, key)
        array.extend(block)
        last_block = block
    return bytes(array)


def decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    array = bytearray()
    last_block = iv
    for i in range(0, len(data), BLOCK_SIZE):
        block = data[i : i + BLOCK_SIZE]
        decrypted_block = aes256_decrypt_block(block, key)
        array.extend(xor(last_block, decrypted_block))
        last_block = block
    return bytes(array)


def alice(channel: Channel, key: bytes) -> None:
    msg = Message("Alice", "Bob", "Here is the top-secret PIN, keep it safe: 42")
    log.info("[Alice] Encrypted: %s", msg)
    iv = os.urandom(BLOCK_SIZE)
    msg.body = iv + encrypt(pkcs7_pad(msg.body, BLOCK_SIZE), key, iv)
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive("Bob")
    iv = msg.body[:BLOCK_SIZE]
    msg.body = pkcs7_unpad(decrypt(msg.body[BLOCK_SIZE:], key, iv), BLOCK_SIZE)
    log.info("[Bob] Decrypted: %s", msg)


def mallory(channel: Channel) -> None:
    channel.peek()


def main() -> None:
    key = os.urandom(32)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    main()
