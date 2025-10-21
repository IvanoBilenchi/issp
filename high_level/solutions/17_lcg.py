# Alice and Bob want to exchange messages over an insecure channel.
# They decide to use a symmetric cipher ensure their confidentiality.
# To make their communication more secure, they opt to use random ephemeral keys (good)
# generated using a Linear Congruential Generator (LCG) (bad), for which
# they previously agreed on the parameters and initial state.
#
# Mallory is an attacker who has access to the communication channel between Alice and Bob.
# Moreover, Mallory:
# - Knows that Alice and Bob are using an LCG for key generation.
# - Has access to several consecutive outputs of their LCG.
# - Knows that the modulus 'm' is either a power of two or a Mersenne prime (2^e - 1).
#
# Your task is to:
# 1. Implement the LCG RNG.
# 2. Allow Mallory to eavesdrop on the communication by breaking the LCG.

from issp import RNG, Actor, ChaCha20, Channel, Message, log, random_int

KEY_SIZE = 32


class LCG(RNG[int]):
    VALUE_SIZE = 4

    def __init__(self, a: int, c: int, m: int) -> None:
        self._a = a
        self._c = c
        self._m = m
        self._state = 12345

    def __next__(self) -> int:
        self._state = (self._a * self._state + self._c) % self._m
        return self._state

    def set_seed(self, seed: int) -> None:
        self._state = seed % self._m


def alice(channel: Channel, rng: LCG) -> None:
    channel = channel.with_stack(ChaCha20(rng.bytes(KEY_SIZE)))
    channel.send(Message("Alice", "Bob", "Hello, Bob!"))


def bob(channel: Channel, rng: LCG) -> None:
    channel = channel.with_stack(ChaCha20(rng.bytes(KEY_SIZE)))
    channel.receive("Bob")


def compute_ac(m: int, x0: int, x1: int, x2: int) -> tuple[int, int]:
    # Eq 1:             x1 = a * x0 + c (mod m)
    # Eq 2:             x2 = a * x1 + c (mod m)
    # From Eq1:         c = x1 - a * x0 (mod m)
    # From Eq2:         x2 = a * x1 + x1 - a * x0 (mod m)
    # Rearranging:      x2 - x1 = a * (x1 - x0) (mod m)
    # Solving for a:    a = (x2 - x1) * (x1 - x0)^(-1) (mod m)
    a = ((x2 - x1) * pow((x1 - x0), -1, m)) % m
    c = (x1 - a * x0) % m
    return a, c


def find_ac(m: int, values: list[int]) -> tuple[int, int]:
    a, c = compute_ac(m, values[0], values[1], values[2])

    # Remember that values contains consecutive outputs of the LCG,
    # so they were generated as: values[i + 1] = (values[i] * a + c) % m
    # To verify that the computed parameters generate the entire sequence of values,
    # we can just check that this holds for all consecutive pairs.
    for i in range(len(values) - 1):
        if (values[i] * a + c) % m != values[i + 1]:
            raise ValueError

    return a, c


def find_lcg_params(values: list[int]) -> tuple[int, int, int]:
    candidate_mods: list[int] = [m for i in range(1, 64) for m in (2**i - 1, 2**i)]

    for m in candidate_mods:
        log.info("[Mallory] Trying m = %d...", m)
        try:
            a, c = find_ac(m, values)
        except ValueError:
            continue
        else:
            log.info("[Mallory] Found LCG params: a = %d, c = %d, m = %d", a, c, m)
            return a, c, m

    err_msg = "Could not find valid LCG params"
    raise ValueError(err_msg)


def mallory(channel: Channel, values: list[int]) -> None:
    # Try to find the LCG parameters from the observed outputs.
    try:
        a, c, m = find_lcg_params(values)
    except ValueError as e:
        log.error("[Mallory] %s", e)
        return

    # Recreate the LCG with the found parameters and synchronize it.
    rng = LCG(a, c, m)
    rng.set_seed(values[-1])

    # Mallory can now generate the same keystream as Alice and Bob.
    channel = channel.with_stack(ChaCha20(rng.bytes(KEY_SIZE)))
    channel.peek()


def main() -> None:
    a, c, m = 16807, 0, 2**31 - 1
    mallory_vals = 10

    alice_rng = LCG(a, c, m)
    bob_rng = LCG(a, c, m)

    for i in range(10):
        log.info("[LCG] Value %d: %d", i + 1, next(alice_rng))

    alice_rng.set_seed(random_int())
    values = [next(alice_rng) for _ in range(mallory_vals)]
    bob_rng.set_seed(values[-1])  # Synchronize Bob's RNG with Alice's last value.

    Actor.start(
        Actor(alice, data=(alice_rng,)),
        Actor(bob, data=(bob_rng,)),
        Actor(mallory, data=(values,), priority=1),
    )


if __name__ == "__main__":
    main()
