# Alice owes a sum of money to Mallory, which she wants to pay back. To do so, they decide
# to register with an online service that will facilitate the transaction.
# To make the authentication more secure, the service requires the use of two-factor
# authentication, where the second factor is a 6 digit one-time password (OTP) generated
# using the HMAC-based One-Time Password (HOTP) algorithm.
#
# Your task is to:
# 1. Implement the HOTP algorithm and integrate it into the authentication protocol.
# 2. Integrate HOTP-based authentication into the existing protocol.
#
# Hints:
# - The starting point for this exercise is the solution to the "naive authentication"
#   exercise. You will need to fix the replay vulnerability by adding HOTP-based authentication.
# - HOTP generation requires truncating the HMAC output in a specific way. For this exercise,
#   you can truncate by taking the first 31 bits of the MAC, after converting it to an integer.
#   This kind of bit manipulation can be done using bitwise operators (in this case, `&`).

import os
from typing import Any

from issp import HMAC, RNG, SHA1, Actor, BankServer, Channel, Message, run_main, scrypt


class HOTP(RNG[int]):
    VALUE_SIZE = 4
    DIGITS = 6

    def __init__(self, key: bytes) -> None:
        self._hmac = HMAC(SHA1(), key)
        self._counter = 0

    def __next__(self) -> int:
        # TO-DO: Implement the HOTP algorithm.
        return self._counter

    def set_seed(self, seed: int) -> None:
        # TO-DO: Implement OTP re-synchronization.
        pass


class Server(BankServer):
    def register(self, sender: str, body: dict[str, Any]) -> bool:
        # TO-DO: Improve user registration by initializing the HOTP generator.
        if sender in self.db:
            return False

        self.db[sender] = {
            "salt": (salt := os.urandom(16)),
            "password": scrypt(body["password"], salt=salt),
            "balance": body["balance"],
        }
        return True

    def authenticate(self, sender: str, body: dict[str, Any]) -> bool:
        # TO-DO: Improve user authentication by verifying the HOTP code.
        if (record := self.db.get(sender)) is None:
            return False
        return scrypt(body["password"], salt=record["salt"]) == record["password"]


def server(channel: Channel) -> None:
    Server("Server", channel).listen()


def alice(channel: Channel) -> None:
    # TO-DO: Initialize the HOTP generator and use it to authenticate.
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
    # TO-DO: Make the message format consistent with Alice's registration.
    message = {
        "action": "register",
        "password": "s3cr3t",
        "balance": 1000.0,
    }
    channel.request(Message("Mallory", "Server", message))

    channel.wait(2)
    msg = channel.peek()

    channel.wait(2)
    channel.send(msg)


def main() -> None:
    Actor.start(Actor(alice), Actor(server, priority=1), Actor(mallory, priority=2))


if __name__ == "__main__":
    run_main(main)
