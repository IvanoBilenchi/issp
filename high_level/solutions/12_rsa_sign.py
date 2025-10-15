# Alice and Bob want to exchange messages over an insecure channel.
# They decide to use digital signatures to ensure their authenticity and integrity.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Implement digital signature generation and verification using RSA and SHA-256.
#
# Hints:
# - Remember that computing and verifying signatures is very similar to computing and verifying
#   MACs based on the encryption of a message digest. The main difference is that
#   signatures use asymmetric cryptography, while MACs use symmetric cryptography.
# - `AsymmetricKey` objects are `Cipher`s, so they have `encrypt` and `decrypt` methods.
# - The `keychain` dictionary maps actor names to their public keys.


from issp import (
    RSA,
    Actor,
    AsymmetricKey,
    Channel,
    Message,
    log,
    sha256,
)

SIGNATURE_SIZE = 256  # RSA-2048 signature size in bytes.


def compute_signature(data: bytes, key: AsymmetricKey) -> bytes:
    return key.encrypt(sha256(data))


def verify(data: bytes, signature: bytes, key: AsymmetricKey) -> bool:
    return sha256(data) == key.decrypt(signature)


def alice(channel: Channel, keychain: dict[str, AsymmetricKey], pri_key: AsymmetricKey) -> None:
    msg = Message("Alice", "Bob", "Hello, Bob!")
    log.info("[Alice] Wants to send: %s", msg)
    msg.body = compute_signature(msg.body, pri_key) + msg.body
    channel.send(msg)


def bob(channel: Channel, keychain: dict[str, AsymmetricKey], pri_key: AsymmetricKey) -> None:
    msg = channel.receive("Bob")
    body = msg.body[SIGNATURE_SIZE:]
    signature = msg.body[:SIGNATURE_SIZE]
    key = keychain[msg.sender]
    if verify(body, signature, key):
        log.info("[Bob] Signature verification succeeded!")
    else:
        log.warning("[Bob] Signature verification failed!")


def mallory(channel: Channel, keychain: dict[str, AsymmetricKey], pri_key: AsymmetricKey) -> None:
    # Toggle this variable to see the difference between eavesdropping and tampering.
    tamper = False

    if not tamper:
        channel.peek()
        return

    msg = channel.receive()
    msg.body = msg.body[:SIGNATURE_SIZE] + b"Screw you, Bob!"
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
    main()
