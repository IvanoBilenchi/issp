# Alice and Bob want to exchange messages over an insecure channel.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Your task is to allow Mallory to:
# 1. Eavesdrop on the communication between Alice and Bob.
# 2. Tamper with the message sent by Alice to Bob.
#
# Hints:
# - Have a look at the documentation of the `Channel` class,
#   especially the `receive`, `send`, and `peek` methods.


from issp import Actor, Channel, Message, run_main


def alice(channel: Channel) -> None:
    msg = Message("Alice", "Bob", b"Hello, Bob!")
    channel.send(msg)


def bob(channel: Channel) -> None:
    channel.receive("Bob")


def mallory(channel: Channel) -> None:
    msg = channel.receive()
    msg.body = "Screw you, Bob!"
    channel.send(msg)


def main() -> None:
    Actor.start(Actor(alice), Actor(bob), Actor(mallory, priority=1))


if __name__ == "__main__":
    run_main(main)
