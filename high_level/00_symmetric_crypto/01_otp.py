# Alice and Bob want to exchange messages over an insecure channel. They decide to do so
# using the One-Time Pad (OTP) encryption algorithm. Luckily, they already share a secret key.
#
# Implement the OTP encryption and decryption functions, and use them
# to ensure the confidentiality of messages exchanged between Alice and Bob.

from issp import Actor, Channel, Message, log, random_bytes, run_main


def alice(channel: Channel, key: bytes) -> None:
    msg = Message(to="Bob", body="Hello, Bob!")
    log.info("Encrypted: %s", msg)
    # TO-DO: Encrypt the message body.
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive()
    # TO-DO: Decrypt the message body.
    log.info("Decrypted: %s", msg)


def mallory(channel: Channel) -> None:
    channel.peek()


def main() -> None:
    key = random_bytes(16)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    run_main(main)
