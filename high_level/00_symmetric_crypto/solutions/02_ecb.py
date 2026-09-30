# Implement the ECB block cipher mode of operation for AES-128 and use it to ensure
# the confidentiality of messages exchanged between Alice and Bob.
#
# Hints:
# - Use the `aes128_encrypt` and `aes128_decrypt` functions from the `issp` module.
# - Remember that we are dealing with a block cipher, so you might need to add padding
#   to the plaintext to make its length a multiple of the block size. For simplicity,
#   you can use zero padding (i.e., append zero bytes to the plaintext), though be aware
#   that this is not a secure padding scheme and it does not account for the case where
#   the plaintext actually ends with zero bytes.

from issp import (
    Actor,
    Channel,
    Message,
    aes128_decrypt,
    aes128_encrypt,
    log,
    random_bytes,
    run_main,
)

BLOCK_SIZE = 16  # AES-128 block size in bytes


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
        array.extend(aes128_encrypt(block, key))
    return bytes(array)


def decrypt(data: bytes, key: bytes) -> bytes:
    array = bytearray()
    for i in range(0, len(data), BLOCK_SIZE):
        block = data[i : i + BLOCK_SIZE]
        array.extend(aes128_decrypt(block, key))
    return bytes(array)


def alice(channel: Channel, key: bytes) -> None:
    msg = Message(to="Bob", body="Here is the top-secret PIN, keep it safe: 42")
    log.info("Encrypted: %s", msg)
    msg.body = encrypt(zero_pad(msg.body, BLOCK_SIZE), key)
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive()
    msg.body = zero_unpad(decrypt(msg.body, key))
    log.info("Decrypted: %s", msg)


def mallory(channel: Channel) -> None:
    channel.peek()


def main() -> None:
    key = random_bytes(16)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    run_main(main)
