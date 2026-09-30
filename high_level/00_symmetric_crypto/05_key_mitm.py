# Alice and Bob want to exchange messages over an insecure channel. They decide to do so
# using the One-Time Pad (OTP) encryption algorithm. However, they do not share a secret key,
# so they must first exchange it. Mallory is listening.
#
# Allow Mallory to:
# 1. Eavesdrop on the communication between Alice and Bob.
# 2. Tamper with the message sent by Alice to Bob.

from issp import Actor, Channel, Message, log, random_bytes, run_main, xor


def encrypt(data: bytes, key: bytes) -> bytes:
    return xor(data, key)


def decrypt(data: bytes, key: bytes) -> bytes:
    return xor(data, key)


def alice(channel: Channel) -> None:
    key = random_bytes(16)
    channel.send(Message(to="Bob", body=key))

    msg = Message(to="Bob", body="Hello, Bob!")
    log.info("Encrypted: %s", msg)
    msg.body = encrypt(msg.body, key)
    channel.send(msg)


def bob(channel: Channel) -> None:
    msg = channel.receive()
    key = msg.body

    msg = channel.receive()
    msg.body = decrypt(msg.body, key)
    log.info("Decrypted: %s", msg)


def mallory(channel: Channel) -> None:
    # TO-DO: Delete this code and implement eavesdropping and tampering.
    channel.peek()
    channel.wait()

    channel.peek()
    channel.wait()


def main() -> None:
    Actor.start(Actor(alice), Actor(bob), Actor(mallory, priority=1))


if __name__ == "__main__":
    run_main(main)
