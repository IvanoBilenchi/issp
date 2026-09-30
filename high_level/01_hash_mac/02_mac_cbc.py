# Alice and Bob want to exchange messages over an insecure channel.
# They decide to use a CBC-MAC to ensure their authenticity and integrity.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Your task is to:
# 1. Implement message authenticity checking using a CBC-MAC scheme based on AES-128.
# 2. Allow Mallory to forge an arbitrary message that passes Bob's authenticity check.
#
# Hints:
# - A CBC-MAC is computed by padding the message to a multiple of the block size,
#   encrypting it in CBC mode with an all-zero IV, and taking the last ciphertext block
#   as the MAC.
# - Refer to the lecture slides for details on how to forge an arbitrary message when the MAC
#   is based on plain CBC.


from issp import Actor, Channel, Message, log, random_bytes, run_main

BLOCK_SIZE = 16


def compute_mac(data: bytes, key: bytes) -> bytes:
    # TO-DO: Compute the MAC.
    return data


def verify(data: bytes, mac: bytes, key: bytes) -> bool:
    # TO-DO: Implement MAC verification.
    return False


def alice(channel: Channel, key: bytes) -> None:
    msg = Message(to="Bob", body="Hello, Bob!")
    log.info("Wants to send: %s", msg)
    # TO-DO: Compute the MAC and prepend it to the message body.
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive()
    # TO-DO: Correctly separate the message body and the MAC.
    body = msg.body
    mac = b""
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

    # TO-DO: Improve Mallory's tampering attempt.
    msg = channel.receive("*")
    msg.body = msg.body[:BLOCK_SIZE] + b"Screw you, Bob!"
    channel.send(msg)


def main() -> None:
    key = random_bytes(16)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    run_main(main)
