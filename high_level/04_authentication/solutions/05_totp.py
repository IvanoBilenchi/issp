# Alice owes a sum of money to Mallory, which she wants to pay back. To do so, they decide
# to register with an online service that will facilitate the transaction.
# To make the authentication more secure, the service requires the use of two-factor
# authentication, where the second factor is a 6 digit one-time password (OTP) generated
# using the Time-based One-Time Password (TOTP) algorithm, which changes every 30 seconds.
#
# Your task is to:
# 1. Implement the TOTP algorithm and integrate it into the authentication protocol.
# 2. Integrate TOTP-based authentication into the existing protocol.
# 3. Verify that the protocol is no longer vulnerable to replay attacks.
#    Is this the case? Why? Can you think of a fix?
#
# Hints:
# - The starting point for this exercise is the solution to the "naive authentication"
#   exercise. You will need to fix the replay vulnerability by adding TOTP-based authentication.

import os
import time
from typing import Any

from issp import HMAC, RNG, SHA1, Actor, BankServer, Channel, Message, run_main, scrypt


class TOTP(RNG[int]):
    VALUE_SIZE = 4
    DIGITS = 6
    PERIOD = 30

    def __init__(self, key: bytes) -> None:
        self._hmac = HMAC(SHA1(), key)
        self._epoch = 0

    def __next__(self) -> int:
        counter = int((time.time() - self._epoch) / self.PERIOD)
        mac = self._hmac.compute_code(counter.to_bytes(8))
        return (int.from_bytes(mac) & 0x7FFFFFFF) % (10**self.DIGITS)

    def set_seed(self, seed: int) -> None:
        self._epoch = seed


class Server(BankServer):
    def register(self, sender: str, body: dict[str, Any]) -> bool:
        if sender in self.db:
            return False

        self.db[sender] = {
            "salt": (salt := os.urandom(16)),
            "password": scrypt(body["password"], salt=salt),
            "otp": TOTP(body["otp_key"]),
            "balance": body["balance"],
        }
        return True

    def authenticate_ex(self, sender: str, body: dict[str, Any]) -> bool:
        if (record := self.db.get(sender)) is None:
            return False
        if scrypt(body["password"], salt=record["salt"]) != record["password"]:
            return False
        return next(record["otp"]) == body["otp"]

    def authenticate(self, sender: str, body: dict[str, Any]) -> bool:
        if (record := self.db.get(sender)) is None:
            return False
        if scrypt(body["password"], salt=record["salt"]) != record["password"]:
            return False
        if body["otp"] == record.get("last_otp") or body["otp"] != next(record["otp"]):
            return False
        record["last_otp"] = body["otp"]
        return True


def server(channel: Channel) -> None:
    Server("Server", channel).listen()


def alice(channel: Channel) -> None:
    password = "p4ssw0rd"
    otp_key = os.urandom(16)
    otp = TOTP(otp_key)
    message = {
        "action": "register",
        "password": password,
        "otp_key": otp_key,
        "balance": 100000.0,
    }
    channel.request(Message("Alice", "Server", message))

    message = {
        "action": "perform_transaction",
        "password": password,
        "otp": next(otp),
        "recipient": "Mallory",
        "amount": 1000.0,
    }
    channel.request(Message("Alice", "Server", message))


def mallory(channel: Channel) -> None:
    message = {
        "action": "register",
        "password": "s3cr3t",
        "otp_key": os.urandom(16),
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
