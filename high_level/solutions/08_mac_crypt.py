# Alice and Bob want to exchange messages over an insecure channel.
# They decide to use a Message Authentication Code (MAC) to ensure their authenticity and integrity.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Implement message authenticity checking using a combination of SHA-256 and ChaCha20.
#
# Hints:
# - You can use the `ChaCha20` class from the `issp` module.
# - The MAC should consist of a random 16-byte IV followed by an encrypted SHA-256 digest.


import os

from issp import Actor, ChaCha20, Channel, Message, log, sha256

DIGEST_SIZE = 32
IV_SIZE = 16
MAC_SIZE = IV_SIZE + DIGEST_SIZE


def compute_mac(data: bytes, key: bytes) -> bytes:
    digest = sha256(data)
    iv = os.urandom(IV_SIZE)
    return iv + ChaCha20(key).encrypt(digest, iv=iv)


def verify(data: bytes, mac: bytes, key: bytes) -> bool:
    iv = mac[:IV_SIZE]
    mac = mac[IV_SIZE:]
    return sha256(data) == ChaCha20(key).decrypt(mac, iv=iv)


def alice(channel: Channel, key: bytes) -> None:
    msg = Message("Alice", "Bob", "Hello, Bob!")
    log.info("[Alice] Wants to send: %s", msg)
    msg.body = compute_mac(msg.body, key) + msg.body
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive("Bob")
    body = msg.body[MAC_SIZE:]
    mac = msg.body[:MAC_SIZE]
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
    msg.body = msg.body[:MAC_SIZE] + b"Screw you, Bob!"
    channel.send(msg)


def main() -> None:
    key = os.urandom(32)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    main()
