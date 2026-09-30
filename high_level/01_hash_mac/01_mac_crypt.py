# Alice and Bob want to exchange messages over an insecure channel.
# They decide to use a Message Authentication Code (MAC) to ensure their authenticity and integrity.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Your task is to:
# 1. Implement message authenticity checking using a combination of SHA-256 and ChaCha20.
# 2. Allow Mallory to forge an arbitrary message that passes Bob's authenticity check.
#
# Hints:
# - You can use the `ChaCha20` class from the `issp` module.
# - The MAC should consist of a random 16-byte IV followed by an encrypted SHA-256 digest.
# - Refer to the lecture slides for details on how to forge an arbitrary message when the MAC
#   is based on a stream cipher.


from issp import Actor, Channel, Message, log, random_bytes, run_main

DIGEST_SIZE = 32
IV_SIZE = 16
MAC_SIZE = IV_SIZE + DIGEST_SIZE


def compute_mac(data: bytes, key: bytes) -> bytes:
    # TO-DO: Compute the MAC using SHA-256 and ChaCha20.
    return data


def verify(data: bytes, mac: bytes, key: bytes) -> bool:
    # TO-DO: Implement MAC verification using SHA-256 and ChaCha20.
    return False


def alice(channel: Channel, key: bytes) -> None:
    msg = Message(to="Bob", body="Hello, Bob!")
    log.info("Wants to send: %s", msg)
    # TO-DO: Compute the MAC and prepend it to the message.
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
    msg.body = msg.body[:MAC_SIZE] + b"Screw you, Bob!"
    channel.send(msg)


def main() -> None:
    key = random_bytes(32)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    run_main(main)
