import random

from ._hash import sha256


class BiometricSensor:
    def __init__(self, actor: str, noise: float = 0.005) -> None:
        self._base = tuple(v / 256 for v in sha256(actor.encode()))
        self._noise = noise

    def acquire_template(self) -> list[float]:
        return [abs(v + random.normalvariate(0, self._noise)) for v in self._base]
