# Alice and Bob want to exchange messages over an insecure channel. They decide to do so
# using the ChaCha20 encryption algorithm. However, they do not share a secret key,
# so they must first exchange it. Luckily, they have access to a trusted
# Key Distribution Center (KDC). Mallory is listening.
#
# Exchange the key through the KDC, and then use it to communicate securely.
#
# Hints:
# - The channel variables are views over the same underlying medium, but each has its own
#   security stack. The stack is used to encode messages before sending them and to decode
#   messages after receiving them. The transformations applied by the stack depend
#   on the layers it contains. As an example, the KDC channel for Alice has a stack that
#   provides both confidentiality and authenticity via AES256 CBC encryption and HMAC-SHA256
#   message authentication.
# - The KDC expects a message from anyone. The message body must be the name of the
#   person with whom the sender wants to communicate. Once the KDC receives such a message,
#   it generates a random key and sends it to both the sender and the recipient.
# - Use the `ChaCha20` class from the `issp` module for encryption and decryption.
#   You may either encrypt and decrypt manually, using the `encrypt` and `decrypt` methods
#   (in which case you will also need to handle the IV), or use the `with_stack` method
#   of the `Channel` class to create a new channel, passing the ChaCha20 layer as the stack.

import os

from issp import AES256, CBC, HMAC, SHA256, Actor, ChaCha20, Channel, Message, Plaintext, log


def alice(plain_channel: Channel, kdc_channel: Channel) -> None:
    kdc_channel.send(Message("Alice", "KDC", "Bob"))
    msg = kdc_channel.receive("Alice")
    key = msg.body

    # The following two implementations are equivalent.
    # Toggle the `use_stack` variable to switch between them.
    use_stack = True

    if use_stack:
        bob_channel = plain_channel.with_stack(ChaCha20(key))
        bob_channel.send(Message("Alice", "Bob", "Hello, Bob!"))
    else:
        cipher = ChaCha20(key)
        iv = os.urandom(16)
        body = iv + cipher.encrypt(b"Hello, Bob!", iv=iv)
        plain_channel.send(Message("Alice", "Bob", body))


def bob(plain_channel: Channel, kdc_channel: Channel) -> None:
    msg = kdc_channel.receive("Bob")
    key = msg.body

    # The following two implementations are equivalent.
    # Toggle the `use_stack` variable to switch between them.
    use_stack = True

    if use_stack:
        alice_channel = plain_channel.with_stack(ChaCha20(key))
        alice_channel.receive("Bob")
    else:
        msg = plain_channel.receive("Bob")
        cipher = ChaCha20(key)
        iv = msg.body[:16]
        msg.body = cipher.decrypt(msg.body[16:], iv=iv)
        log.info("[Bob] Decrypted: %s", msg)


def kdc(plain_channel: Channel, alice_channel: Channel, bob_channel: Channel) -> None:
    channels = {"Alice": alice_channel, "Bob": bob_channel}

    log.info("[KDC] Listening...")
    while True:
        msg = plain_channel.receive("KDC", timeout=10.0)

        if msg.is_empty:
            break

        if msg.sender not in channels:
            continue

        key = os.urandom(32)
        sender = msg.sender
        sender_channel = channels[sender]
        msg = sender_channel.stack.decode(msg)
        log.info("[KDC] Decoded: %s", msg)
        recipient = msg.body.decode()
        recipient_channel = channels[recipient]

        sender_channel.send(Message("KDC", sender, key))
        recipient_channel.send(Message("KDC", recipient, key))


def mallory(channel: Channel) -> None:
    while True:
        if channel.peek(timeout=5.0).is_empty:
            break
        channel.wait()


def main() -> None:
    plain = Plaintext()
    alice_kdc_stack = CBC(AES256()) | HMAC(SHA256())
    bob_kdc_stack = CBC(AES256()) | HMAC(SHA256())
    Actor.start(
        Actor(alice, stacks=(plain, alice_kdc_stack)),
        Actor(bob, stacks=(plain, bob_kdc_stack)),
        Actor(kdc, name="KDC", stacks=(plain, alice_kdc_stack, bob_kdc_stack)),
        Actor(mallory, priority=1),
    )


if __name__ == "__main__":
    main()
