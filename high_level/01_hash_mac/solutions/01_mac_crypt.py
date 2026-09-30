# Alice and Bob want to exchange messages over an insecure channel.
# They decide to use a Message Authentication Code (MAC) to ensure their authenticity and integrity.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Your task is to:
# 1. Implement message authenticity checking using a combination of SHA-256 and ChaCha20.
# 2. Allow Mallory to forge an arbitrary message that passes Bob's authenticity check.
#
# Hints:
# - You can use the `ChaCha20` class from the `issp` module.
# - The MAC should consist of a random 16-byte IV followed by an encrypted SHA-256 digest.
# - Refer to the lecture slides for details on how to forge an arbitrary message when the MAC
#   is based on a stream cipher.


from issp import Actor, ChaCha20, Channel, Message, log, random_bytes, run_main, sha256, xor

DIGEST_SIZE = 32
IV_SIZE = 16
MAC_SIZE = IV_SIZE + DIGEST_SIZE


def compute_mac(data: bytes, key: bytes) -> bytes:
    digest = sha256(data)
    iv = random_bytes(IV_SIZE)
    return iv + ChaCha20(key).encrypt(digest, iv=iv)


def verify(data: bytes, mac: bytes, key: bytes) -> bool:
    iv = mac[:IV_SIZE]
    mac = mac[IV_SIZE:]
    return sha256(data) == ChaCha20(key).decrypt(mac, iv=iv)


def alice(channel: Channel, key: bytes) -> None:
    msg = Message(to="Bob", body="Hello, Bob!")
    log.info("Wants to send: %s", msg)
    msg.body = compute_mac(msg.body, key) + msg.body
    channel.send(msg)


def bob(channel: Channel, key: bytes) -> None:
    msg = channel.receive()
    body = msg.body[MAC_SIZE:]
    mac = msg.body[:MAC_SIZE]
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
    iv = msg.body[:IV_SIZE]
    old_mac = msg.body[IV_SIZE:MAC_SIZE]
    old_msg_body = msg.body[MAC_SIZE:]

    new_msg_body = b"Screw you, Bob!"
    new_mac = xor(old_mac, sha256(old_msg_body), sha256(new_msg_body))
    msg.body = iv + new_mac + new_msg_body
    channel.send(msg)


def main() -> None:
    key = random_bytes(32)
    Actor.start(Actor(alice, data=(key,)), Actor(bob, data=(key,)), Actor(mallory, priority=1))


if __name__ == "__main__":
    run_main(main)
