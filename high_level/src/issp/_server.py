from typing import TYPE_CHECKING, Any

from . import _log as log
from ._comm import Channel, Message, Plaintext

if TYPE_CHECKING:
    from collections.abc import Callable


class Handler:
    type Func = Callable[[str, dict[str, Any]], dict[str, Any]]

    def __init__(self, func: Func, *, auth: bool = True) -> None:
        self.func = func
        self.auth = auth

    def __call__(self, sender: str, body: dict[str, Any]) -> dict[str, Any]:
        return self.func(sender, body)


class Server:
    def __init__(
        self,
        name: str,
        channels: Channel | dict[str, Channel],
    ) -> None:
        self.name = name
        self._handlers: dict[str, Handler] = {}

        if isinstance(channels, Channel):
            self.plain = channels
            self.channels = {}
        else:
            self.plain = next(iter(channels.values())).with_stack(Plaintext())
            self.channels = channels

        self.add_handler("register", self._register, auth=False)

    def register(self, sender: str, body: dict[str, Any]) -> bool:
        raise NotImplementedError

    def authenticate(self, sender: str, body: dict[str, Any]) -> bool:
        raise NotImplementedError

    def authorize(self, sender: str, body: dict[str, Any]) -> bool:
        raise NotImplementedError

    def add_handler(self, action: str, handler: Handler.Func, *, auth: bool = True) -> None:
        self._handlers[action] = Handler(handler, auth=auth)

    def listen(self) -> None:
        log.info("[%s] Listening...", self.name)
        while msg := self._receive():
            sender, channel, body = self._decode(msg)
            response = self._handle(sender, body)
            channel.send(Message(self.name, sender, response))

    def _register(self, sender: str, body: dict[str, Any]) -> dict[str, Any]:
        return {"status": "success" if self.register(sender, body) else "failure"}

    def _receive(self) -> Message:
        return self.plain.receive(self.name, timeout=10.0, quiet=True)

    def _decode(self, msg: Message) -> tuple[str, Channel, dict[str, Any]]:
        channel = self.channels.get(msg.sender, self.plain)
        msg = channel.stack.decode(msg)
        log.info("[%s] Received: %s", self.name, msg)
        return msg.sender, channel, msg.json_dict()

    def _handle(self, sender: str, body: dict[str, Any]) -> dict[str, Any]:
        response: dict[str, Any] = {}
        try:
            action = body["action"]
            response["action"] = action
            handler = self._handlers[action]
            if handler.auth:
                if not self.authenticate(sender, body):
                    return response | {"status": "authentication failure"}
                if not self.authorize(sender, body):
                    return response | {"status": "authorization failure"}
            return response | handler(sender, body)
        except Exception as e:
            log.warning("[%s] %s", self.name, e)
            return response | {"status": "error"}


class BankServer(Server):
    def authorize(self, sender: str, body: dict[str, Any]) -> bool:
        del sender, body  # Unused
        return True

    def __init__(self, name: str, channels: Channel | dict[str, Channel]) -> None:
        super().__init__(name, channels)
        self.db: dict[str, dict[str, Any]] = {}
        self.add_handler("perform_transaction", self._perform_transaction)

    def _perform_transaction(self, sender: str, body: dict[str, Any]) -> dict[str, Any]:
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


class FileServer(Server):
    def __init__(self, name: str, channels: Channel | dict[str, Channel]) -> None:
        super().__init__(name, channels)
        self.files: dict[str, str] = {}
        self.add_handler("read", self._read)
        self.add_handler("write", self._write)

    def register(self, sender: str, body: dict[str, Any]) -> bool:
        del sender, body  # Unused
        return True

    def authenticate(self, sender: str, body: dict[str, Any]) -> bool:
        del sender, body  # Unused
        return True

    def _read(self, sender: str, body: dict[str, Any]) -> dict[str, Any]:
        del sender  # Unused
        if data := self.files.get(body["path"]):
            return {"status": "success", "data": data}
        return {"status": "not found"}

    def _write(self, sender: str, body: dict[str, Any]) -> dict[str, Any]:
        del sender  # Unused
        self.files[body["path"]] += body["data"]
        return {"status": "success"}
