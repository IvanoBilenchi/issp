# Alice and Bob want to exchange messages over an insecure channel.
# They decide to use HMAC to ensure their authenticity and integrity, but they opt
# to use a 4-digit PIN instead of a randomly generated key so that it is easier to remember.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Allow Mallory to obtain the key by brute-forcing the first message,
# and then use it to tamper with the second message.
#
# Hints:
# - Use the `generate_bytes` function of the `issp` module to generate possible keys.
# - Assume that Mallory knows that the key is a 4-digit PIN.


from issp import HMAC, Actor, Channel, Message, generate_bytes, log, run_main


def alice(channel: Channel) -> None:
    channel.send(Message("Alice", "Bob", "Hello, Bob!"))
    channel.send(Message("Alice", "Bob", "How are you?"))


def bob(channel: Channel) -> None:
    channel.receive("Bob")
    channel.receive("Bob")


def mallory(channel: Channel) -> None:
    msg = channel.peek()
    hmac = HMAC()
    body = msg.body[hmac.code_size :]
    existing_mac = msg.body[: hmac.code_size]

    for key in generate_bytes(length=4, charset="0123456789"):
        hmac.key = key
        if hmac.compute_code(body) == existing_mac:
            log.info("[Mallory] Found key: %s", key)
            break
    channel.wait()

    msg = channel.receive()
    msg.body = "Screw you, Bob!"
    msg.body = hmac.compute_code(msg.body) + msg.body
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
