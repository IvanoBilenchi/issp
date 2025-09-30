# Alice and Bob want to exchange messages over an insecure channel.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Your task is to allow Mallory to:
# 1. Eavesdrop on the communication between Alice and Bob.
# 2. Tamper with the message sent by Alice to Bob.
#
# Hints:
# - Use the `peek` method of the channel to eavesdrop on messages before they are delivered.


from issp import Channel, Message, start_actors


def alice(channel: Channel) -> None:
    msg = Message("Alice", "Bob", b"Hello, Bob!")
    channel.send(msg)


def bob(channel: Channel) -> None:
    channel.receive("Bob")


def mallory(channel: Channel) -> None:
    msg = channel.peek()
    msg.body = b"Screw you, Bob!"
    channel.send(msg)


if __name__ == "__main__":
    start_actors(alice, bob, mallory)
