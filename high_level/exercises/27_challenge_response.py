# Alice owes a sum of money to Mallory, which she wants to pay back. To do so, they decide
# to register with an online service that will facilitate the transaction.
# To make the authentication more secure, the service adopts a password-based
# challenge-response protocol.
#
# Your task is to implement the challenge-response protocol according to the following spec:
# - h = scrypt
# - f = h(challenge || h(password))
# - challenge = random 16-byte nonce
#
# Hints:
# - The endpoint to request the challenge is the "request_transaction" action.
# - You can obtain a JSON representation of a message's body using the `json_dict()` method.
# - Since passwords are salted, you need to return the salt along with the challenge.

import os
from typing import Any

from issp import Actor, BankServer, Channel, Message, run_main, scrypt


class Server(BankServer):
    def __init__(self, name: str, channels: Channel | dict[str, Channel]) -> None:
        super().__init__(name, channels)
        self.handlers["request_transaction"] = self._challenge

    def _challenge(self, sender: str, body: dict[str, Any]) -> dict[str, Any]:
        del body  # Unused
        return self.challenge(sender)

    def register(self, sender: str, body: dict[str, Any]) -> bool:
        if sender in self.db:
            return False

        self.db[sender] = {
            "salt": (salt := os.urandom(16)),
            "password": scrypt(body["password"], salt=salt),
            "balance": body["balance"],
        }
        return True

    def challenge(self, sender: str) -> dict[str, Any]:
        # TO-DO: Implement challenge generation and return the challenge along with the salt.
        return {"challenge": b"", "salt": b""}

    def authenticate(self, sender: str, body: dict[str, Any]) -> bool:
        # TO-DO: Implement response verification.
        return False


def server(channel: Channel) -> None:
    Server("Server", channel).listen()


def alice(channel: Channel) -> None:
    password = "p4ssw0rd"
    msg = {
        "action": "register",
        "password": password,
        "balance": 100000.0,
    }
    channel.request(Message("Alice", "Server", msg))

    # TO-DO: Implement Alice's behavior according to the challenge-response protocol.
    msg = {
        "action": "perform_transaction",
        "recipient": "Mallory",
        "amount": 1000.0,
    }
    channel.request(Message("Alice", "Server", msg))


def mallory(channel: Channel) -> None:
    message = {
        "action": "register",
        "password": "s3cr3t",
        "balance": 1000.0,
    }
    channel.request(Message("Mallory", "Server", message))


def main() -> None:
    Actor.start(Actor(alice), Actor(server, priority=1), Actor(mallory, priority=2))


if __name__ == "__main__":
    run_main(main)
