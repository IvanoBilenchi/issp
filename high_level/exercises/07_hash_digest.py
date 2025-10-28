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


from issp import Actor, Channel, Message, log, run_main

DIGEST_SIZE = 32  # SHA-256 produces a 32-byte hash.


def verify(data: bytes, digest: bytes) -> bool:
    # TO-DO: Implement message integrity verification using SHA-256.
    return False


def alice(channel: Channel) -> None:
    msg = Message("Alice", "Bob", "Hello, Bob!")
    log.info("[Alice] Wants to send: %s", msg)
    # TO-DO: Compute the SHA-256 hash of the message body and prepend it to the message.
    channel.send(msg)


def bob(channel: Channel) -> None:
    msg = channel.receive("Bob")
    # TO-DO: Correctly separate the message body and the digest.
    body = msg.body
    digest = b""
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
    # TO-DO: Improve Mallory's tampering attempt.
    msg.body = msg.body[DIGEST_SIZE:] + b"Screw you, Bob!"
    channel.send(msg)


def main() -> None:
    Actor.start(Actor(alice), Actor(bob), Actor(mallory, priority=1))


if __name__ == "__main__":
    run_main(main)
