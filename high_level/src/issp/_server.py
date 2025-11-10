from typing import TYPE_CHECKING, Any

from . import _log as log
from ._comm import Channel, Message, Plaintext

if TYPE_CHECKING:
    from collections.abc import Callable


class Server:
    def __init__(
        self,
        name: str,
        channels: Channel | dict[str, Channel],
    ) -> None:
        self.name = name
        self.handlers: dict[str, Callable[[str, dict[str, Any]], dict[str, Any]]] = {}

        if isinstance(channels, Channel):
            self.plain = channels
            self.channels = {}
        else:
            self.plain = next(iter(channels.values())).with_stack(Plaintext())
            self.channels = channels

    def listen(self) -> None:
        log.info("[%s] Listening...", self.name)
        while self._handle_request():
            pass

    def _handle_request(self) -> bool:
        if (msg := self.plain.receive(self.name, timeout=10.0, quiet=True)).is_empty:
            return False

        channel = self.channels.get(msg.sender, self.plain)
        action = None

        try:
            msg = channel.stack.decode(msg)
            log.info("[%s] Received: %s", self.name, msg)
            body = msg.json_dict()
            action = body["action"]
            response = self.handlers[action](msg.sender, body)
        except Exception as e:
            log.warning("[%s] %s", self.name, e)
            response = {"status": "error"}

        if action:
            response = {"action": action} | response

        channel.send(Message(self.name, msg.sender, response))
        return True


class BankServer(Server):
    def register(self, sender: str, body: dict[str, Any]) -> bool:
        raise NotImplementedError

    def authenticate(self, sender: str, body: dict[str, Any]) -> bool:
        raise NotImplementedError

    def __init__(self, name: str, channels: Channel | dict[str, Channel]) -> None:
        super().__init__(name, channels)
        self.db: dict[str, dict[str, Any]] = {}
        self.handlers["register"] = self._register
        self.handlers["perform_transaction"] = self._perform_transaction

    def _register(self, sender: str, body: dict[str, Any]) -> dict[str, Any]:
        return {"status": "success" if self.register(sender, body) else "failure"}

    def _perform_transaction(self, sender: str, body: dict[str, Any]) -> dict[str, Any]:
        if not self.authenticate(sender, body):
            return {"status": "authentication failure"}

        recipient = body["recipient"]
        user_record = self.db[sender]
        recipient_record = self.db[recipient]
        amount = body["amount"]

        if amount <= 0:
            return {"status": "invalid amount"}

        if user_record["balance"] < amount:
            return {"status": "insufficient funds"}

        user_record["balance"] -= amount
        recipient_record["balance"] += amount

        log.info(
            "[%s] Current balances: %s",
            self.name,
            {k: v["balance"] for k, v in self.db.items()},
        )

        return {"status": "success", "recipient": recipient, "amount": amount}
