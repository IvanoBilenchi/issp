# Alice and Bob want to exchange messages over an insecure channel.
# They decide to use a keyed hash MAC to ensure their authenticity and integrity.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Implement message authenticity checking using a keyed hash MAC scheme based on SHA-256.
#
# Hints:
# - Compute the MAC as SHA-256(key || message || key), as seen in the lecture.


from issp import Actor, Channel, Message, log, random_bytes, run_main

MAC_SIZE = 32


def compute_mac(data: bytes, key: bytes) -> bytes:
    # TO-DO: Compute the MAC.
    return data


def verify(data: bytes, mac: bytes, key: bytes) -> bool:
    # TO-DO: Implement MAC verification.
    return False


def alice(channel: Channel, key: bytes) -> None:
    msg = Message(to="Bob", body="Hello, Bob!")
    log.info("Wants to send: %s", msg)
    # TO-DO: Compute the MAC and prepend it to the message.
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive()
    # TO-DO: Correctly separate the message body and the MAC.
    body = msg.body
    mac = b""
    if verify(body, mac, key):
        log.info("Message authentication check succeeded!")
    else:
        log.warning("Message authentication check failed!")


def mallory(channel: Channel) -> None:
    # Toggle this variable to switch between eavesdropping and tampering.
    tamper = False

    if not tamper:
        channel.peek()
        return

    msg = channel.receive("*")
    msg.body = msg.body[:MAC_SIZE] + b"Screw you, Bob!"
    channel.send(msg)


def main() -> None:
    key = random_bytes(32)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    run_main(main)
