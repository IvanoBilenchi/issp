# Alice and Bob want to exchange messages over an insecure channel.
# They decide to use HMAC to ensure their authenticity and integrity, but they opt to use
# a 4-digit PIN instead of a randomly generated key, so that it is easier to remember.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Your task is to allow Mallory to obtain the key by brute-forcing the HMAC of the first
# message, and then use it to tamper with the second message.
#
# Hints:
# - Use the `generate_bytes` function of the `issp` module to generate possible keys.
# - Assume that Mallory knows that the key is a 4-digit PIN.


from issp import HMAC, Actor, Channel, Message, log, run_main


def alice(channel: Channel) -> None:
    channel.send(Message(to="Bob", body="Hello, Bob!"))
    channel.send(Message(to="Bob", body="How are you?"))


def bob(channel: Channel) -> None:
    channel.receive()
    channel.receive()


def mallory(channel: Channel) -> None:
    msg = channel.peek()
    # TO-DO: Brute-force the key by trying all possible 4-digit PINs.
    channel.wait()

    msg = channel.receive("*")
    msg.body = "Screw you!"
    # TO-DO: Prepend the correct HMAC to the tampered message.
    channel.send(msg)


def main() -> None:
    key = b"1234"
    log.info("Key: %s", key)
    alice_bob = HMAC(key=key)
    Actor.start(
        Actor(alice, stacks=(alice_bob,)),
        Actor(bob, stacks=(alice_bob,)),
        Actor(mallory, priority=1),
    )


if __name__ == "__main__":
    run_main(main)
