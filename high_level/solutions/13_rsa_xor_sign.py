# Alice and Bob want to exchange messages over an insecure channel.
# They decide to use RSA signatures to ensure their authenticity and integrity, though they
# feel adventurous and decide to implement their own hash function based on XOR.
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
#
# Your task is to:
# 1. Implement an 8 bytes XOR hash function.
# 2. Allow Mallory to forge an arbitrary message that passes Bob's authenticity check.
#
# Hints:
# - The XOR hash function should process the input data in 8-byte blocks, XORing
#   each block with the current hash value (starting from zero).
# - Refer to the lecture slides for details on how to forge an arbitrary message
#   when the hash function is based on XOR.


from issp import RSA, Actor, Channel, Hash, Message, Signature, xor, zero_pad

SIGNATURE_SIZE = 256


class XOR8(Hash):
    CODE_SIZE = 8

    def compute_code(self, data: bytes) -> bytes:
        data = zero_pad(data, self.CODE_SIZE)
        code = bytes(self.CODE_SIZE)
        for i in range(0, len(data), self.CODE_SIZE):
            code = xor(code, data[i : i + self.CODE_SIZE])
        return code


def alice(channel: Channel) -> None:
    channel.send(Message("Alice", "Bob", "Hello, Bob!"))


def bob(channel: Channel) -> None:
    channel.receive("Bob")


def mallory(channel: Channel) -> None:
    msg = channel.receive()
    new_body = b"Screw you, Bob!"
    new_body = zero_pad(new_body, XOR8.CODE_SIZE)

    signature = msg.body[:SIGNATURE_SIZE]
    orig_body = msg.body[SIGNATURE_SIZE:]

    xor8 = XOR8()
    new_digest = xor8.compute_code(new_body)
    orig_digest = xor8.compute_code(orig_body)

    msg.body = signature + new_body + xor(new_digest, orig_digest)
    channel.send(msg)


def main() -> None:
    alice_pri_key, alice_pub_key = RSA.generate_key_pair()
    alice_bob = Signature(alice_pri_key, XOR8())
    bob_alice = Signature(alice_pub_key, XOR8())
    Actor.start(
        Actor(alice, stacks=(alice_bob,)),
        Actor(bob, stacks=(bob_alice,)),
        Actor(mallory, priority=1),
    )


if __name__ == "__main__":
    main()
