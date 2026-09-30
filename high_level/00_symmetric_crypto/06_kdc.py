# Alice and Bob want to exchange messages over an insecure channel. They decide to do so
# using the ChaCha20 encryption algorithm. However, they do not share a secret key,
# so they must first exchange it. Luckily, they have access to a trusted
# Key Distribution Center (KDC). Mallory is listening.
#
# Your task is to have Alice and Bob obtain a shared key through the KDC, and then use it
# to communicate securely.
#
# Hints:
# - The channel parameters are views over the same underlying medium, but each has its own
#   security stack, which encodes messages before sending them and decodes them after
#   receiving them. What the stack does depends on the layers it contains. For example,
#   the KDC channel of Alice has a stack that provides both confidentiality and authenticity
#   through AES-128 CBC encryption and HMAC-SHA256 message authentication.
# - To request a key, send a message to the KDC over your KDC channel. The message body must
#   be the name of the actor you want to communicate with. The KDC then generates a random key
#   and sends it to both the sender and the recipient over their respective KDC channels.
# - Use the `ChaCha20` class from the `issp` module for encryption and decryption.
#   You may either call its `encrypt` and `decrypt` methods directly (in which case you will
#   also need to handle the IV), or pass a ChaCha20 layer to the `with_stack` method
#   of the `Channel` class to obtain a channel that encrypts and decrypts automatically.

from issp import (
    AES128,
    CBC,
    HMAC,
    SHA256,
    Actor,
    Channel,
    Message,
    Plaintext,
    log,
    random_bytes,
    run_main,
)


def alice(plain_channel: Channel, kdc_channel: Channel) -> None:
    # TO-DO: Request a key from the KDC to communicate with Bob,
    #        then use it to send him a message.
    pass


def bob(plain_channel: Channel, kdc_channel: Channel) -> None:
    # TO-DO: Receive the key from the KDC, then use it to receive
    #        and decrypt the message from Alice.
    pass


def kdc(plain_channel: Channel, alice_channel: Channel, bob_channel: Channel) -> None:
    channels = {"Alice": alice_channel, "Bob": bob_channel}

    log.info("Listening...")
    while True:
        msg = plain_channel.receive(timeout=10.0)

        if msg.is_empty:
            break

        if msg.sender not in channels:
            continue

        key = random_bytes(32)
        sender = msg.sender
        sender_channel = channels[sender]
        msg = sender_channel.stack.decode(msg)
        log.info("Decoded: %s", msg)
        recipient = msg.body.decode()
        recipient_channel = channels[recipient]

        sender_channel.send(Message(to=sender, body=key))
        recipient_channel.send(Message(to=recipient, body=key))


def mallory(channel: Channel) -> None:
    while True:
        if channel.peek(timeout=5.0).is_empty:
            break
        channel.wait()


def main() -> None:
    plain = Plaintext()
    alice_kdc_stack = CBC(AES128()) | HMAC(SHA256())
    bob_kdc_stack = CBC(AES128()) | HMAC(SHA256())
    Actor.start(
        Actor(alice, stacks=(plain, alice_kdc_stack)),
        Actor(bob, stacks=(plain, bob_kdc_stack)),
        Actor(kdc, name="KDC", stacks=(plain, alice_kdc_stack, bob_kdc_stack)),
        Actor(mallory, priority=1),
    )


if __name__ == "__main__":
    run_main(main)
