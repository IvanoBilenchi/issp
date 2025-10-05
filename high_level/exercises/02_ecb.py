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

from issp import Actor, Channel, Message, log

BLOCK_SIZE = 16  # AES256 block size in bytes


def zero_pad(data: bytes, block_size: int) -> bytes:
    # TO-DO: Implement zero padding.
    return data


def zero_unpad(data: bytes) -> bytes:
    # TO-DO: Implement zero unpadding.
    return data


def encrypt(data: bytes, key: bytes) -> bytes:
    # TO-DO: Implement AES256 ECB encryption.
    return data


def decrypt(data: bytes, key: bytes) -> bytes:
    # TO-DO: Implement AES256 ECB decryption.
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
