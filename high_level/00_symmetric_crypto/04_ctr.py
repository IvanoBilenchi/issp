# Implement the CTR block cipher mode of operation for AES-128 and use it to ensure
# the confidentiality of messages exchanged between Alice and Bob.
#
# Hints:
# - Since CTR mode turns a block cipher into a stream cipher, no padding is needed.
# - Remember that, for stream ciphers, both encryption and decryption consist of XORing
#   the data with the keystream.

from issp import Actor, Channel, Message, log, random_bytes, run_main

BLOCK_SIZE = 16


def key_stream(key: bytes, iv: bytes, length: int) -> bytes:
    # TO-DO: Implement the AES-128 CTR keystream.
    # This function should return at least `length` keystream bytes.
    return key


# [Optional]: If you are familiar with Python generators, you can instead implement
# an unbounded keystream function that yields an infinite sequence of keystream bytes.
# This is useful for processing data of unknown length, and it is more memory efficient,
# since it does not need to store the entire keystream in memory.
#
# See the `CTR` class of the `issp` module for an example implementation.
#
# def key_stream(key: bytes, iv: bytes) -> Iterator[int]:
#     while True:
#         byte = <compute next keystream byte>
#         yield byte


def encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    # TO-DO: Implement AES-128 CTR encryption.
    return data


def decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    # TO-DO: Implement AES-128 CTR decryption.
    return data


def alice(channel: Channel, key: bytes) -> None:
    msg = Message(to="Bob", body="Here is the top-secret PIN, keep it safe: 42")
    log.info("Wants to send: %s", msg)
    # TO-DO: Encrypt the message body.
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive()
    # TO-DO: Decrypt the message body.
    log.info("Decrypted: %s", msg)


def mallory(channel: Channel) -> None:
    channel.peek()


def main() -> None:
    key = random_bytes(16)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    run_main(main)
