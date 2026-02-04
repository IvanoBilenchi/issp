# Implement the CTR block cipher mode of operation for AES256 and use it to ensure
# the confidentiality of messages exchanged between Alice and Bob.
#
# Hints:
# - Since CTR mode turns a block cipher into a stream cipher, no padding is needed.
# - Remember that both encryption and decryption for stream ciphers can be implemented
#   as the XOR of the data with the keystream.

import os
from collections.abc import Iterator

from issp import Actor, Channel, Message, aes256_encrypt_block, log, run_main, xor

BLOCK_SIZE = 16


def key_stream(key: bytes, iv: bytes, length: int) -> bytes:
    stream = bytearray()
    counter = int.from_bytes(iv)
    while len(stream) < length:
        stream.extend(aes256_encrypt_block(counter.to_bytes(BLOCK_SIZE), key))
        counter += 1
    return bytes(stream)


# Alternative keystream implementation using Python generators.
def key_stream_unbounded(key: bytes, iv: bytes) -> Iterator[int]:
    counter = int.from_bytes(iv)
    while True:
        yield from aes256_encrypt_block(counter.to_bytes(BLOCK_SIZE), key)
        counter += 1


def encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    return xor(data, key_stream(key, iv, len(data)))


def decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    return xor(data, key_stream(key, iv, len(data)))


def alice(channel: Channel, key: bytes) -> None:
    msg = Message("Alice", "Bob", "Here is the top-secret PIN, keep it safe: 42")
    log.info("[Alice] Encrypted: %s", msg)
    iv = os.urandom(BLOCK_SIZE)
    msg.body = iv + encrypt(msg.body, key, iv)
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive("Bob")
    iv = msg.body[:BLOCK_SIZE]
    msg.body = decrypt(msg.body[BLOCK_SIZE:], key, iv)
    log.info("[Bob] Decrypted: %s", msg)


def mallory(channel: Channel) -> None:
    channel.peek()


def main() -> None:
    key = os.urandom(32)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    run_main(main)
