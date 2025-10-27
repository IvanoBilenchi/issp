# Alice owes a sum of money to Mallory, which she wants to pay back. To do so, they decide
# to register with an online service that will facilitate the transaction.
# Alice communicates with the service over an encrypted and authenticated channel, so
# she is confident that Mallory cannot do anything malicious during the communication.
#
# Your task is to:
# 1. Implement a naive authentication protocol where the user authenticates by sending
#    a username and password to the server. The server should store the password hashed
#    and salted using a slow hash function.
# 2. Help Mallory attack the protocol by replaying Alice's transaction request.
#
# Hints:
# - In this exercise, message bodies are represented as dictionaries. They are serialized
#   and deserialized automatically as JSON by the `issp` library, so you don't need to worry
#   about that.
# - The `Server` class has a `db` dictionary attribute that you can use to store user records.

from typing import Any

from issp import (
    HMAC,
    Actor,
    BankServer,
    ChaCha20,
    Channel,
    Message,
)


class Server(BankServer):
    def register(self, sender: str, body: dict[str, Any]) -> bool:
        # TO-DO: Implement user registration. Return True on success, False on failure.
        return False

    def authenticate(self, sender: str, body: dict[str, Any]) -> bool:
        # TO-DO: Implement user authentication. Return True on success, False on failure.
        return False


def server(alice_channel: Channel) -> None:
    Server("Server", {"Alice": alice_channel}).listen()


def alice(channel: Channel) -> None:
    password = "p4ssw0rd"
    message = {
        "action": "register",
        "password": password,
        "balance": 100000.0,
    }
    channel.request(Message("Alice", "Server", message))

    message = {
        "action": "perform_transaction",
        "password": password,
        "recipient": "Mallory",
        "amount": 1000.0,
    }
    channel.request(Message("Alice", "Server", message))


def mallory(channel: Channel) -> None:
    message = {
        "action": "register",
        "password": "s3cr3t",
        "balance": 1000.0,
    }
    channel.request(Message("Mallory", "Server", message))

    # TO-DO: Replace the following lines with a replay attack of Alice's transaction.
    channel.wait(2)
    channel.peek()


def main() -> None:
    alice_server = ChaCha20() | HMAC()
    Actor.start(
        Actor(alice, stacks=(alice_server,)),
        Actor(server, stacks=(alice_server,), priority=1),
        Actor(mallory, priority=2),
    )


if __name__ == "__main__":
    main()
