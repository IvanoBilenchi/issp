# Alice and Bob want to exchange messages over an insecure channel.
# They decide to use digital envelopes to ensure their confidentiality.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Your task is to:
# 1. Implement a digital envelope scheme using RSA and ChaCha20.
# 2. Allow Mallory to tamper with the communication. Can she also eavesdrop? Why?


import os

from issp import RSA, Actor, AsymmetricKey, ChaCha20, Channel, Message, log, run_main


def encrypt(data: bytes, rsa_key: AsymmetricKey) -> bytes:
    key = os.urandom(ChaCha20.KEY_SIZE)
    iv = os.urandom(ChaCha20.IV_SIZE)
    cipher = ChaCha20(key)
    return rsa_key.encrypt(key + iv) + cipher.encrypt(data, iv=iv)


def decrypt(data: bytes, rsa_key: AsymmetricKey) -> bytes:
    key_iv = rsa_key.decrypt(data[: rsa_key.key_size])
    ciphertext = data[rsa_key.key_size :]
    key = key_iv[: ChaCha20.KEY_SIZE]
    iv = key_iv[ChaCha20.KEY_SIZE :]
    return ChaCha20(key).decrypt(ciphertext, iv=iv)


def alice(channel: Channel, keychain: dict[str, AsymmetricKey], pri_key: AsymmetricKey) -> None:
    msg = Message("Alice", "Bob", "Hello, Bob!")
    log.info("[Alice] Encrypted: %s", msg)
    msg.body = encrypt(msg.body, keychain[msg.recipient])
    channel.send(msg)


def bob(channel: Channel, keychain: dict[str, AsymmetricKey], pri_key: AsymmetricKey) -> None:
    msg = channel.receive("Bob")
    msg.body = decrypt(msg.body, pri_key)
    log.info("[Bob] Decrypted: %s", msg)


def mallory(channel: Channel, keychain: dict[str, AsymmetricKey], pri_key: AsymmetricKey) -> None:
    msg = channel.receive()
    new_body = b"Screw you, Bob!"
    msg.body = encrypt(new_body, keychain[msg.recipient])
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
