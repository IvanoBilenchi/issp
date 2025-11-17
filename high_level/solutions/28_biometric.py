# Alice owes a sum of money to Mallory, which she wants to pay back. To do so, they decide
# to register with an online service that will facilitate the transaction.
# The service adopts a biometric challenge-response protocol for authentication.
# It compares biometric templates via Euclidean distance, and adopts a threshold of 0.95.
#
# Your task is to:
# - Implement the challenge-response protocol according to the following spec:
#   - E = ChaCha20
#   - Challenge = random 16-byte nonce
# - Implement biometric identification.
#
# Hints:
# - Alice communicates with the service using ChaCha20, so you don't need to add encryption.
# - Each actor has a `BiometricSensor` that can be used to acquire biometric templates
#   using the `acquire_template()` method.
# - You can turn distances into similarity scores using the formula: 1 / (1 + distance)

import os
from typing import Any

from issp import (
    Actor,
    BankServer,
    BiometricSensor,
    ChaCha20,
    Channel,
    Message,
    run_main,
)


def euclidean_distance(a: list[float], b: list[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b, strict=True)) ** 0.5


def similarity(a: list[float], b: list[float]) -> float:
    return 1 / (1 + euclidean_distance(a, b))


class Server(BankServer):
    def __init__(self, name: str, channels: Channel | dict[str, Channel]) -> None:
        super().__init__(name, channels)
        self.add_handler("request_transaction", self._challenge, auth=False)
        self.add_handler("identify", self._identify, auth=False)

    def _challenge(self, sender: str, body: dict[str, Any]) -> dict[str, Any]:
        del body  # Unused
        return self.challenge(sender)

    def _identify(self, sender: str, body: dict[str, Any]) -> dict[str, Any]:
        del sender  # Unused
        user = self.identify(body["template"])
        return {"status": "success", "user": user} if user else {"status": "not found"}

    def register(self, sender: str, body: dict[str, Any]) -> bool:
        if sender in self.db:
            return False

        self.db[sender] = {
            "template": body["template"],
            "balance": body["balance"],
        }
        return True

    def challenge(self, sender: str) -> dict[str, Any]:
        challenge = os.urandom(16)
        self.db[sender]["challenge"] = challenge
        return {"challenge": challenge}

    def authenticate(self, sender: str, body: dict[str, Any]) -> bool:
        if (record := self.db.get(sender)) is None:
            return False
        if body["challenge"] != record["challenge"]:
            return False
        return similarity(body["template"], record["template"]) > 0.95

    def identify(self, template: list[float]) -> str | None:
        best = (None, 0.95)
        for user, record in self.db.items():
            if score := similarity(template, record["template"]) > best[1]:
                best = (user, score)
        return best[0]


def server(alice_channel: Channel, mallory_channel: Channel) -> None:
    Server("Server", {"Alice": alice_channel, "Mallory": mallory_channel}).listen()


def alice(channel: Channel, sensor: BiometricSensor) -> None:
    msg = {
        "action": "register",
        "template": sensor.acquire_template(),
        "balance": 100000.0,
    }
    channel.request(Message("Alice", "Server", msg))

    msg = {
        "action": "identify",
        "template": sensor.acquire_template(),
    }
    channel.request(Message("Alice", "Server", msg))

    msg = {"action": "request_transaction"}
    msg = channel.request(Message("Alice", "Server", msg)).json_dict()

    msg = {
        "action": "perform_transaction",
        "challenge": msg["challenge"],
        "template": sensor.acquire_template(),
        "recipient": "Mallory",
        "amount": 1000.0,
    }
    channel.request(Message("Alice", "Server", msg))


def mallory(channel: Channel, sensor: BiometricSensor) -> None:
    message = {
        "action": "register",
        "template": sensor.acquire_template(),
        "balance": 1000.0,
    }
    channel.request(Message("Mallory", "Server", message))


def main() -> None:
    alice_server = ChaCha20()
    mallory_server = ChaCha20()
    alice_sensor = BiometricSensor("Alice")
    mallory_sensor = BiometricSensor("Mallory")
    Actor.start(
        Actor(alice, stacks=(alice_server,), data=(alice_sensor,)),
        Actor(server, stacks=(alice_server, mallory_server), priority=1),
        Actor(mallory, stacks=(mallory_server,), data=(mallory_sensor,), priority=2),
    )


if __name__ == "__main__":
    run_main(main)
