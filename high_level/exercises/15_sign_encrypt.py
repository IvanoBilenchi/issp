# Alice and Bob want to exchange messages over an insecure channel.
#
# Ensure that their communication is confidential, authentic, and non-repudiable.
# You must use both a stream cipher and an asymmetric cipher.


import os

from issp import RSA, Actor, AsymmetricKey, Channel, Message, log

IV_SIZE = 16
SIGNATURE_SIZE = 256


def alice(
    channel: Channel,
    keychain: dict[str, AsymmetricKey],
    pri_key: AsymmetricKey,
    sym_key: bytes,
) -> None:
    msg = Message("Alice", "Bob", "Hello, Bob!")
    log.info("[Alice] Wants to send: %s", msg)
    # TO-DO: Implement.
    channel.send(msg)


def bob(
    channel: Channel,
    keychain: dict[str, AsymmetricKey],
    pri_key: AsymmetricKey,
    sym_key: bytes,
) -> None:
    msg = channel.receive("Bob")
    # TO-DO: Implement.
    log.info("[Bob] Recovered: %s", msg)


def mallory(channel: Channel) -> None:
    channel.peek()


def main() -> None:
    alice_pri_key, alice_pub_key = RSA.generate_key_pair()
    bob_pri_key, bob_pub_key = RSA.generate_key_pair()
    keychain = {"Alice": alice_pub_key, "Bob": bob_pub_key}
    sym_key = os.urandom(32)
    Actor.start(
        Actor(alice, data=(keychain, alice_pri_key, sym_key)),
        Actor(bob, data=(keychain, bob_pri_key, sym_key)),
        Actor(mallory, priority=1),
    )


if __name__ == "__main__":
    main()
