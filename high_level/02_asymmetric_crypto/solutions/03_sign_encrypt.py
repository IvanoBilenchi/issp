# Alice and Bob want to exchange messages over an insecure channel.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Your task is to ensure that their communication is confidential, authentic,
# and non-repudiable, using both a stream cipher and an asymmetric cipher.
#
# Hints:
# - Alice and Bob already share a symmetric key (`sym_key`), and each of them has an RSA
#   key pair. The `keychain` dictionary maps actor names to their public keys.


from issp import (
    RSA,
    Actor,
    AsymmetricKey,
    ChaCha20,
    Channel,
    Message,
    log,
    random_bytes,
    run_main,
    sha256,
)

IV_SIZE = 16
SIGNATURE_SIZE = 256


def alice(
    channel: Channel,
    keychain: dict[str, AsymmetricKey],
    pri_key: AsymmetricKey,
    sym_key: bytes,
) -> None:
    msg = Message(to="Bob", body="Hello, Bob!")
    log.info("Wants to send: %s", msg)

    # Encrypt.
    iv = random_bytes(IV_SIZE)
    msg.body = iv + ChaCha20(sym_key).encrypt(msg.body, iv=iv)

    # Sign.
    digest = sha256(msg.body)
    signature = pri_key.encrypt(digest)
    msg.body = signature + msg.body

    channel.send(msg)


def bob(
    channel: Channel,
    keychain: dict[str, AsymmetricKey],
    pri_key: AsymmetricKey,
    sym_key: bytes,
) -> None:
    msg = channel.receive()

    # Verify signature.
    signature = msg.body[:SIGNATURE_SIZE]
    body = msg.body[SIGNATURE_SIZE:]
    digest = sha256(body)
    if digest != keychain[msg.sender].decrypt(signature):
        err_msg = "Signature verification failed!"
        raise ValueError(err_msg)

    # Decrypt.
    iv = body[:IV_SIZE]
    ciphertext = body[IV_SIZE:]
    msg.body = ChaCha20(sym_key).decrypt(ciphertext, iv=iv)

    log.info("Recovered: %s", msg)


def mallory(channel: Channel) -> None:
    channel.peek()


def main() -> None:
    alice_pri_key, alice_pub_key = RSA.generate_key_pair()
    bob_pri_key, bob_pub_key = RSA.generate_key_pair()
    keychain = {"Alice": alice_pub_key, "Bob": bob_pub_key}
    sym_key = random_bytes(32)
    Actor.start(
        Actor(alice, data=(keychain, alice_pri_key, sym_key)),
        Actor(bob, data=(keychain, bob_pri_key, sym_key)),
        Actor(mallory, priority=1),
    )


if __name__ == "__main__":
    run_main(main)
