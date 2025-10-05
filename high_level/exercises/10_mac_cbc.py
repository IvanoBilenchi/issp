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

from issp import Actor, Channel, Message, log

BLOCK_SIZE = 16


def compute_mac(data: bytes, key: bytes) -> bytes:
    # TO-DO: Compute the MAC.
    return data


def verify(data: bytes, mac: bytes, key: bytes) -> bool:
    # TO-DO: Implement MAC verification.
    return False


def alice(channel: Channel, key: bytes) -> None:
    msg = Message("Alice", "Bob", "Hello, Bob!")
    log.info("[Alice] Wants to send: %s", msg)
    # TO-DO: Compute the MAC and prepend it to the message.
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive("Bob")
    # TO-DO: Correctly separate the message body and the MAC.
    body = msg.body
    mac = b""
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
