# Alice owes a sum of money to Mallory, which she wants to pay back. To do so, they decide
# to register with an online service that will facilitate the transaction.
# The service adopts a biometric challenge-response protocol for authentication.
# Two biometric templates match if their similarity score is greater than 0.95.
#
# Your task is to:
# 1. Implement the challenge-response protocol according to the following spec:
#    - E = ChaCha20
#    - Challenge = random 16-byte nonce
# 2. Implement biometric identification, i.e., finding the registered user whose template
#    best matches a given one.
#
# Hints:
# - Alice's channel with the service is already encrypted with ChaCha20,
#   so you don't need to add encryption yourself.
# - Each actor has a `BiometricSensor`, whose `acquire_template()` method
#   acquires a biometric template.
# - Compute the similarity score of two templates as 1 / (1 + d), where d is
#   the Euclidean distance between them.

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
    def __init__(self, channels: Channel | dict[str, Channel]) -> None:
        super().__init__(channels)
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
        # TO-DO: Implement challenge generation and return the challenge.
        return {"challenge": b""}

    def authenticate(self, sender: str, body: dict[str, Any]) -> bool:
        # TO-DO: Implement biometric authentication with challenge verification.
        return False

    def identify(self, template: list[float]) -> str | None:
        # TO-DO: Implement biometric identification.
        return None


def server(alice_channel: Channel, mallory_channel: Channel) -> None:
    Server({"Alice": alice_channel, "Mallory": mallory_channel}).listen()


def alice(channel: Channel, sensor: BiometricSensor) -> None:
    msg = {
        "action": "register",
        "template": sensor.acquire_template(),
        "balance": 100000.0,
    }
    channel.request(Message(to="Server", body=msg))

    msg = {
        "action": "identify",
        "template": sensor.acquire_template(),
    }
    channel.request(Message(to="Server", body=msg))

    # TO-DO: Implement Alice's behavior according to the biometric challenge-response protocol.
    msg = {
        "action": "perform_transaction",
        "recipient": "Mallory",
        "amount": 1000.0,
    }
    channel.request(Message(to="Server", body=msg))


def mallory(channel: Channel, sensor: BiometricSensor) -> None:
    message = {
        "action": "register",
        "template": sensor.acquire_template(),
        "balance": 1000.0,
    }
    channel.request(Message(to="Server", body=message))


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
