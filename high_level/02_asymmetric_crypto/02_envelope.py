# Alice and Bob want to exchange messages over an insecure channel.
# They decide to use digital envelopes to ensure their confidentiality.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Your task is to:
# 1. Implement a digital envelope scheme using RSA and ChaCha20.
# 2. Allow Mallory to tamper with the communication. Can she also eavesdrop? Why?


from issp import RSA, Actor, AsymmetricKey, Channel, Message, log, run_main


def encrypt(data: bytes, rsa_key: AsymmetricKey) -> bytes:
    # TO-DO: Implement digital envelope encryption using RSA and ChaCha20.
    return data


def decrypt(data: bytes, rsa_key: AsymmetricKey) -> bytes:
    # TO-DO: Implement digital envelope decryption using RSA and ChaCha20.
    return data


def alice(channel: Channel, keychain: dict[str, AsymmetricKey], pri_key: AsymmetricKey) -> None:
    msg = Message("Alice", "Bob", "Hello, Bob!")
    log.info("[Alice] Encrypted: %s", msg)
    # TO-DO: Create and send a digital envelope.
    channel.send(msg)


def bob(channel: Channel, keychain: dict[str, AsymmetricKey], pri_key: AsymmetricKey) -> None:
    msg = channel.receive("Bob")
    # TO-DO: Open the digital envelope.
    log.info("[Bob] Decrypted: %s", msg)


def mallory(channel: Channel, keychain: dict[str, AsymmetricKey], pri_key: AsymmetricKey) -> None:
    msg = channel.receive()
    new_body = b"Screw you, Bob!"
    # TO-DO: Tamper with the message.
    msg.body = new_body
    channel.send(msg)


def main() -> None:
    alice_pri_key, alice_pub_key = RSA.generate_key_pair()
    bob_pri_key, bob_pub_key = RSA.generate_key_pair()
    mallory_pri_key, mallory_pub_key = RSA.generate_key_pair()
    keychain = {"Alice": alice_pub_key, "Bob": bob_pub_key, "Mallory": mallory_pub_key}
    Actor.start(
        Actor(alice, data=(keychain, alice_pri_key)),
        Actor(bob, data=(keychain, bob_pri_key)),
        Actor(mallory, data=(keychain, mallory_pri_key), priority=1),
    )


if __name__ == "__main__":
    run_main(main)
