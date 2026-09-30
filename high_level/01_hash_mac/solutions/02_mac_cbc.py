# Alice and Bob want to exchange messages over an insecure channel.
# They decide to use a CBC-MAC to ensure their authenticity and integrity.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Your task is to:
# 1. Implement message authenticity checking using a CBC-MAC scheme based on AES-128.
# 2. Allow Mallory to forge an arbitrary message that passes Bob's authenticity check.
#
# Hints:
# - A CBC-MAC is computed by encrypting the message in CBC mode with a zero IV
#   and taking the last ciphertext block as the MAC.
# - Refer to the lecture slides for details on how to forge an arbitrary message when the MAC
#   is based on plain CBC.


from issp import (
    Actor,
    Channel,
    Message,
    aes128_encrypt,
    log,
    pkcs7_pad,
    random_bytes,
    run_main,
    xor,
)

BLOCK_SIZE = 16


def compute_mac(data: bytes, key: bytes) -> bytes:
    data = pkcs7_pad(data, BLOCK_SIZE)
    last_block = bytes(BLOCK_SIZE)
    for i in range(0, len(data), BLOCK_SIZE):
        block = data[i : i + BLOCK_SIZE]
        block = aes128_encrypt(xor(last_block, block), key)
        last_block = block
    return last_block


def verify(data: bytes, mac: bytes, key: bytes) -> bool:
    return mac == compute_mac(data, key)


def alice(channel: Channel, key: bytes) -> None:
    msg = Message(to="Bob", body="Hello, Bob!")
    log.info("Wants to send: %s", msg)
    msg.body = compute_mac(msg.body, key) + msg.body
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive()
    body = msg.body[BLOCK_SIZE:]
    mac = msg.body[:BLOCK_SIZE]
    if verify(body, mac, key):
        log.info("Message authentication check succeeded!")
    else:
        log.warning("Message authentication check failed!")


def mallory(channel: Channel) -> None:
    # Toggle this variable to switch between eavesdropping and tampering.
    tamper = False

    if not tamper:
        channel.peek()
        return

    msg = channel.receive("*")
    msg.body = msg.body[:BLOCK_SIZE] + b"Screw you, Bob!"
    channel.send(msg)


def main() -> None:
    key = random_bytes(16)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    run_main(main)
