# Encrypt the communication between Alice and Bob using the ChaCha20 stream cipher.
#
# Hint: Have a look at the cryprography.hazmat.primitives.ciphers module.
# Docs: https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption

import os

from cryptography.hazmat.primitives import ciphers
from cryptography.hazmat.primitives.ciphers import algorithms

from issp import Actor, Channel, EncryptionLayer, SymmetricCipher


class ChaCha(SymmetricCipher):
    iv_size = 16

    def encrypt(self, message: bytes, iv: bytes) -> bytes:
        cipher = ciphers.Cipher(algorithms.ChaCha20(self.key, iv), mode=None)
        return cipher.encryptor().update(message)

    def decrypt(self, message: bytes, iv: bytes) -> bytes:
        cipher = ciphers.Cipher(algorithms.ChaCha20(self.key, iv), mode=None)
        return cipher.decryptor().update(message)


def main() -> None:
    alice = Actor("Alice")
    bob = Actor("Bob")
    mallory = Actor("Mallory", quiet=False)

    channel = Channel()
    alice_bob_layer = EncryptionLayer(channel, ChaCha(os.urandom(32)))

    alice.send(alice_bob_layer, b"Hello, Bob! - Alice")
    mallory.receive(channel)
    bob.receive(alice_bob_layer)


if __name__ == "__main__":
    main()
