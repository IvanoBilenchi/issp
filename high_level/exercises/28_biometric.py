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


class Server(BankServer):
    def __init__(self, name: str, channels: Channel | dict[str, Channel]) -> None:
        super().__init__(name, channels)
        self.handlers["request_transaction"] = self._challenge
        self.handlers["identify"] = self._identify

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
        # TO-DO: Implement challenge generation and return the challenge.
        return {"challenge": b""}

    def authenticate(self, sender: str, body: dict[str, Any]) -> bool:
        # TO-DO: Implement biometric authentication with challenge verification.
        return False

    def identify(self, template: list[float]) -> str | None:
        # Implement biometric identification.
        return None


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

    # TO-DO: Implement Alice's behavior according to the biometric challenge-response protocol.
    msg = {
        "action": "perform_transaction",
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
