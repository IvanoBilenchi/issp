# Implement the CBC block cipher mode of operation for AES-128 and use it to ensure
# the confidentiality of messages exchanged between Alice and Bob.
#
# Hints:
# - Use the `aes128_encrypt` and `aes128_decrypt` functions from the `issp` module.
# - For padding, you may use the `pkcs7_pad` and `pkcs7_unpad` functions from the `issp`
#   module, which implement an unambiguous padding scheme.

from issp import (
    Actor,
    Channel,
    Message,
    aes128_decrypt,
    aes128_encrypt,
    log,
    pkcs7_pad,
    pkcs7_unpad,
    random_bytes,
    run_main,
    xor,
)

BLOCK_SIZE = 16


def encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    array = bytearray()
    last_block = iv
    for i in range(0, len(data), BLOCK_SIZE):
        block = data[i : i + BLOCK_SIZE]
        block = xor(last_block, block)
        block = aes128_encrypt(block, key)
        array.extend(block)
        last_block = block
    return bytes(array)


def decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    array = bytearray()
    last_block = iv
    for i in range(0, len(data), BLOCK_SIZE):
        block = data[i : i + BLOCK_SIZE]
        decrypted_block = aes128_decrypt(block, key)
        array.extend(xor(last_block, decrypted_block))
        last_block = block
    return bytes(array)


def alice(channel: Channel, key: bytes) -> None:
    msg = Message(to="Bob", body="Here is the top-secret PIN, keep it safe: 42")
    log.info("Wants to send: %s", msg)
    iv = random_bytes(BLOCK_SIZE)
    msg.body = iv + encrypt(pkcs7_pad(msg.body, BLOCK_SIZE), key, iv)
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive()
    iv = msg.body[:BLOCK_SIZE]
    msg.body = pkcs7_unpad(decrypt(msg.body[BLOCK_SIZE:], key, iv), BLOCK_SIZE)
    log.info("Decrypted: %s", msg)


def mallory(channel: Channel) -> None:
    channel.peek()


def main() -> None:
    key = random_bytes(16)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    run_main(main)
