# Implement the CTR block cipher mode of operation for AES256 and use it to ensure
# the confidentiality of messages exchanged between Alice and Bob.
#
# Hints:
# - Since CTR mode turns a block cipher into a stream cipher, no padding is needed.
# - Remember that both encryption and decryption for stream ciphers can be implemented
#   as the XOR of the data with the keystream.

import os

from issp import Actor, Channel, Message, log

BLOCK_SIZE = 16


def key_stream(key: bytes, iv: bytes, length: int) -> bytes:
    # TO-DO: Implement the AES256 CTR keystream.
    # This function should return at least `length` keystream bytes.
    return key


# [Optional]: If you're experienced with Python generators, you can instead implement
# an unbounded version of the keystream function that produces an infinite sequence
# of keystream bytes. This can be useful for decrypting data of unknown length, and it is also
# more memory efficient since it does not require storing the entire keystream in memory.
#
# See the `CTR` class of the `issp` module for an example implementation.
#
# def key_stream(key: bytes, iv: bytes) -> Iterator[int]:
#    while True:
#        byte = <compute next keystream byte>
#        yield byte


def encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    # TO-DO: Implement AES256 CTR encryption.
    return data


def decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    # TO-DO: Implement AES256 CTR decryption.
    return data


def alice(channel: Channel, key: bytes) -> None:
    msg = Message("Alice", "Bob", "Here is the top-secret PIN, keep it safe: 42")
    log.info("[Alice] Encrypted: %s", msg)
    # TO-DO: Encrypt the message body.
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive("Bob")
    # TO-DO: Decrypt the message body.
    log.info("[Bob] Decrypted: %s", msg)


def mallory(channel: Channel) -> None:
    channel.peek()


def main() -> None:
    key = os.urandom(32)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    main()
