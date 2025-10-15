# Alice and Bob want to exchange messages over an insecure channel.
# They decide to use a CBC-MAC to ensure their authenticity and integrity.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Implement message authenticity checking using a CBC-MAC scheme based on AES256.
#
# Hints:
# - A CBC-MAC is computed by encrypting the message in CBC mode with a zero IV
#   and taking the last ciphertext block as the MAC.


import os

from issp import Actor, Channel, Message, aes256_encrypt_block, log, pkcs7_pad, xor

BLOCK_SIZE = 16


def compute_mac(data: bytes, key: bytes) -> bytes:
    data = pkcs7_pad(data, BLOCK_SIZE)
    last_block = bytes(BLOCK_SIZE)
    for i in range(0, len(data), BLOCK_SIZE):
        block = data[i : i + BLOCK_SIZE]
        block = aes256_encrypt_block(xor(last_block, block), key)
        last_block = block
    return last_block


def verify(data: bytes, mac: bytes, key: bytes) -> bool:
    return mac == compute_mac(data, key)


def alice(channel: Channel, key: bytes) -> None:
    msg = Message("Alice", "Bob", "Hello, Bob!")
    log.info("[Alice] Wants to send: %s", msg)
    msg.body = compute_mac(msg.body, key) + msg.body
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive("Bob")
    body = msg.body[BLOCK_SIZE:]
    mac = msg.body[:BLOCK_SIZE]
    if verify(body, mac, key):
        log.info("[Bob] Message authentication check succeeded!")
    else:
        log.warning("[Bob] Message authentication check failed!")


def mallory(channel: Channel) -> None:
    # Toggle this variable to see the difference between eavesdropping and tampering.
    tamper = False

    if not tamper:
        channel.peek()
        return

    msg = channel.receive()
    msg.body = msg.body[:BLOCK_SIZE] + b"Screw you, Bob!"
    channel.send(msg)


def main() -> None:
    key = os.urandom(32)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    main()
