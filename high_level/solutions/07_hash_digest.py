# Alice and Bob want to exchange messages over an insecure channel.
# They decide to use a hash function to ensure their integrity.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Your task is to:
# 1. Implement message integrity checking using the SHA-256 hash function.
# 2. Allow Mallory to successfully tamper with the message without being detected.
#
# Hints:
# - You can use the `sha256` function or the `SHA256` class from the `issp` module.


from issp import Actor, Channel, Message, log, sha256

DIGEST_SIZE = 32  # SHA-256 produces a 32-byte (256-bit) hash


def verify(data: bytes, digest: bytes) -> bool:
    return sha256(data) == digest


def alice(channel: Channel) -> None:
    msg = Message("Alice", "Bob", "Hello, Bob!")
    log.info("[Alice] Wants to send: %s", msg)
    msg.body = sha256(msg.body) + msg.body
    channel.send(msg)


def bob(channel: Channel) -> None:
    msg = channel.receive("Bob")
    body = msg.body[DIGEST_SIZE:]
    digest = msg.body[:DIGEST_SIZE]
    if verify(body, digest):
        log.info("[Bob] Message integrity check succeeded!")
    else:
        log.warning("[Bob] Message integrity check failed!")


def mallory(channel: Channel) -> None:
    # Toggle this variable to see the difference between eavesdropping and tampering.
    tamper = False

    if not tamper:
        channel.peek()
        return

    msg = channel.receive()
    body = b"Screw you, Bob!"
    msg.body = sha256(body) + body
    channel.send(msg)


def main() -> None:
    Actor.start(Actor(alice), Actor(bob), Actor(mallory, priority=1))


if __name__ == "__main__":
    main()
