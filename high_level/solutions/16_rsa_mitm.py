# Alice and Bob want to exchange messages over an insecure channel.
# They decide to use digital signatures to ensure their authenticity and integrity.
# However, they do not have a trusted way to share their public keys, so they must do so
# over the same insecure channel.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Allow Mallory to impersonate Alice when communicating with Bob.


from issp import RSA, Actor, Channel, Message, Signature


def alice(channel: Channel) -> None:
    # Key exchange.
    pri_key, pub_key = RSA.generate_key_pair()
    channel.send(Message("Alice", "Bob", pub_key.key_bytes))

    # Secure channel setup.
    channel = channel.with_stack(Signature(pri_key))
    channel.send(Message("Alice", "Bob", "Hello, Bob!"))


def bob(channel: Channel) -> None:
    # Key exchange.
    msg = channel.receive("Bob")
    alice_pub_key = RSA.load_public_key(msg.body)

    # Secure channel setup.
    channel = channel.with_stack(Signature(alice_pub_key))
    channel.receive("Bob")


def mallory(channel: Channel) -> None:
    pri_key, pub_key = RSA.generate_key_pair()
    channel.receive()
    channel.send(Message("Alice", "Bob", pub_key.key_bytes))

    # Optional: wait for Alice's message and discard it before sending her own.
    # channel.wait()
    # channel.receive()

    channel = channel.with_stack(Signature(pri_key))
    channel.send(Message("Alice", "Bob", "Screw you, Bob!"))


def main() -> None:
    Actor.start(Actor(alice), Actor(bob), Actor(mallory, priority=1))


if __name__ == "__main__":
    main()
