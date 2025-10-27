from __future__ import annotations

import base64
import itertools
import json
import threading
import time
from typing import TYPE_CHECKING

from . import _log as log

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from typing import Any


type JSONBody = ComplexBody | str
type ComplexBody = dict[str, Any] | list[Any]
type SimpleBody = bytes | str
type Body = ComplexBody | SimpleBody


class Message:
    """A message exchanged between entities over a communication channel."""

    @staticmethod
    def encode_body(body: Body) -> bytes:
        """
        Encode the body of the message into bytes.

        :param body: The body of the message.
        :return: The encoded body as bytes.
        """
        if isinstance(body, bytes | bytearray):
            return bytes(body)
        if isinstance(body, str) and (data := _from_utf8(body)):
            return data
        if isinstance(body, (dict, list)) and (data := _from_json(body)):
            return data
        return str(body).encode()

    @staticmethod
    def decode_body(data: bytes) -> Body:
        """
        Decode the body of the message from bytes.

        :param data: The body of the message as bytes.
        :return: The decoded body.
        """
        if body := _to_json(data):
            return body
        if body := _to_utf8(data):
            return body
        return data

    @classmethod
    def empty(cls) -> Message:
        """
        Create an empty message.

        :return: An empty message instance.
        """
        return cls("", "", b"")

    @property
    def is_empty(self) -> bool:
        """
        Check if the message is empty.

        :return: True if the message is empty, False otherwise.
        """
        return not (self.sender or self.recipient or self.body)

    @property
    def body(self) -> bytes:
        """The body of the message, represented as bytes."""
        return self._body

    @body.setter
    def body(self, value: Body) -> None:
        """
        Set the body of the message.

        :param value: The new body of the message.
        """
        self._body = self.encode_body(value)

    def __init__(self, sender: str, recipient: str, body: Body) -> None:
        """
        Initialize a message.

        :param sender: The sender of the message.
        :param recipient: The recipient of the message.
        :param body: The body of the message.
        """
        self.sender = sender
        """The sender of the message."""
        self.recipient = recipient
        """The recipient of the message."""
        self.body = body

    def __repr__(self) -> str:
        body = self.decode_body(self.body)
        return f"Message(from={self.sender!r}, to={self.recipient!r}, body={body!r})"

    def copy(self, body: Body | None = None) -> Message:
        """
        Create a copy of the message, optionally replacing the body.

        :param body: The new body for the copied message. If None, the original body is used.
        :return: A new message instance.
        """
        return Message(self.sender, self.recipient, body or self.body)

    def json_dict(self) -> dict[str, Any]:
        """
        Get the body of the message decoded as a JSON-compatible dictionary.

        :return: The body of the message as a JSON-compatible dictionary.
        """
        body = _to_json(self.body)
        if not isinstance(body, dict):
            err_msg = "Message body is not a JSON object"
            raise ValueError(err_msg)  # noqa: TRY004
        return body

    def json_list(self) -> list[Any]:
        """
        Get the body of the message decoded as a JSON-compatible list.

        :return: The body of the message as a JSON-compatible list.
        """
        body = _to_json(self.body)
        if not isinstance(body, list):
            err_msg = "Message body is not a JSON array"
            raise ValueError(err_msg)  # noqa: TRY004
        return body


class Channel:
    """
    A shared communication channel that provides synchronized access to an underlying medium.

    .. note::
        This class manages message transmission and reception between entities by synchronizing
        access to the underlying medium through a queue-based system. For each time interval,
        a write request is dequeued and processed, followed by a read request, and so on.

        Both read and write operations are blocking, ensuring that only one operation of each type
        is processed per interval. Additionally, read requests may be further blocked if they are
        waiting for a message addressed to a specific recipient.

        Note that the channel may block indefinitely if no messages are sent or if the expected
        messages are not received.
    """

    @property
    def stack(self) -> Stack:
        """The security stack applied to messages sent and received through this channel."""
        return self._stack

    def __init__(
        self,
        name: str,
        medium: Medium,
        stack: Layer,
        priority: int = 0,
    ) -> None:
        self._stack = Stack(stack)
        self._medium = medium
        self._name = name
        self._priority = priority

    def _get_priority(self, override: int | None) -> int:
        return self._priority if override is None else override

    def send(
        self,
        msg: Message,
        *,
        priority: int | None = None,
        timeout: float | None = None,
        quiet: bool = False,
    ) -> None:
        """
        Send a message through the communication medium.

        :param msg: The message to be sent.
        :param priority: The priority level for writing to the medium.
                         If None, an instance-specific default priority is used.
        :param timeout: The maximum time to wait for a message, in seconds.
        """
        try:
            enc_msg = self.stack.encode(msg.copy())
            self._medium.write(enc_msg, self._get_priority(priority), timeout=timeout)
        except Exception as e:
            log.warning("[%s] %s", self._name, e)
            return
        if not quiet:
            log.info("[%s] Sent: %s", self._name, msg)

    def receive(
        self,
        recipient: str | None = None,
        *,
        priority: int | None = None,
        timeout: float | None = None,
        quiet: bool = False,
    ) -> Message:
        """
        Receive a message from the communication medium.

        After calling this method, the message is removed from the medium.
        If you wish to read a message without removing it, consider using the `peek` method instead.

        :param recipient: The intended recipient of the message.
                          If None, any message can be received.
        :param priority: The priority level for reading from the medium.
                         If None, an instance-specific default priority is used.
        :param timeout: The maximum time to wait for a message, in seconds.
        :return: The received message.
        """
        try:
            msg = self._medium.read(recipient, self._get_priority(priority), timeout=timeout)
            msg = self.stack.decode(msg)
        except Exception as e:
            log.warning("[%s] %s", self._name, e)
            return Message.empty()
        if not quiet:
            log.info("[%s] Received: %s", self._name, msg)
        return msg

    def peek(
        self,
        *,
        priority: int | None = None,
        timeout: float | None = None,
        quiet: bool = False,
    ) -> Message:
        """
        Peek at a message in the communication medium without removing it.

        :param priority: The priority level for reading from the medium.
                         If None, an instance-specific default priority is used.
        :param timeout: The maximum time to wait for a message, in seconds.
        :return: The peeked message.
        """
        try:
            priority = self._get_priority(priority)
            msg = self._medium.read(Event.PEEK_TOKEN, priority, clear=False, timeout=timeout)
            msg = self.stack.decode(msg)
        except Exception as e:
            log.warning("[%s] %s", self._name, e)
            return Message.empty()
        if not quiet:
            log.info("[%s] Peeked: %s", self._name, msg)
        return msg

    def request(
        self,
        msg: Message,
        *,
        priority: int | None = None,
        timeout: float | None = None,
        quiet: bool = False,
    ) -> Message:
        """
        Send a message and wait for a response.

        :param msg: The message to be sent.
        :param priority: The priority level for writing to and reading from the medium.
                         If None, an instance-specific default priority is used.
        :param timeout: The maximum time to wait for a response, in seconds.
        :return: The received response message.
        """
        self.send(msg, priority=priority, timeout=timeout, quiet=quiet)
        return self.receive(msg.sender, priority=priority, timeout=timeout, quiet=quiet)

    def wait(self, ticks: int = 1) -> None:
        """
        Wait for a specified number of ticks (time intervals) on the communication medium.

        :param ticks: The number of ticks to wait.
        """
        self._medium.wait(ticks)

    def with_stack(self, stack: Layer) -> Channel:
        """
        Create a new channel over the same medium but with a different security stack.

        :param stack: The new security stack.
        :return: New channel instance.
        """
        return Channel(self._name, self._medium, stack, self._priority)


class Layer:
    """A base class for defining security layers that can be stacked to form a security stack."""

    def __or__(self, base: object) -> Stack:
        if not isinstance(base, Layer):
            err_msg = f"Unsupported operand type(s) for |: '{type(self)}' and '{type(base)}'"
            raise TypeError(err_msg)
        return Stack(self, base)

    def encode(self, msg: Message) -> Message:
        """
        Encode a message by applying the layer's encoding logic.

        :param msg: The message to be encoded.
        :return: The encoded message.
        """
        raise NotImplementedError

    def decode(self, msg: Message) -> Message:
        """
        Decode a message by applying the layer's decoding logic.

        :param msg: The message to be decoded.
        :return: The decoded message.
        """
        raise NotImplementedError


class Plaintext(Layer):
    """A security layer that performs no transformations on messages."""

    def encode(self, msg: Message) -> Message:
        return msg

    def decode(self, msg: Message) -> Message:
        return msg


class Stack(Layer):
    """A stack of security layers that can be applied to messages for encoding and decoding."""

    @property
    def layers(self) -> Sequence[Layer]:
        """The list of layers in the stack."""
        return (*self._layers,)

    def __init__(self, *layers: Layer) -> None:
        """
        Initialize a stack of security layers.

        :param layers: The layers to be included in the stack.
        """
        self._layers: list[Layer] = []
        for layer in layers:
            if isinstance(layer, Stack):
                self._layers.extend(layer.layers)
            elif not isinstance(layer, Plaintext):
                self._layers.append(layer)

    def __len__(self) -> int:
        return len(self._layers)

    def __getitem__(self, index: int) -> Layer:
        return self._layers[index]

    def encode(self, msg: Message) -> Message:
        """
        Encode a message by sequentially applying the encoding logic of each layer in the stack.

        :param msg: The message to be encoded.
        :return: The encoded message.
        """
        for layer in self._layers:
            msg = layer.encode(msg)
        return msg

    def decode(self, msg: Message) -> Message:
        """
        Decode a message by sequentially applying the decoding logic of each layer in the stack.

        :param msg: The message to be decoded.
        :return: The decoded message.
        """
        for layer in reversed(self._layers):
            msg = layer.decode(msg)
        return msg


class Actor:
    @staticmethod
    def start(*args: Actor, interval: float = 1.0) -> None:
        medium = Medium(interval=interval)
        threads: list[threading.Thread] = []
        for a in args:
            channels = tuple(Channel(a.name, medium, s, a.priority) for s in a.stacks)
            thread = threading.Thread(target=a.target, args=(*channels, *a.data), daemon=True)
            threads.append(thread)
            thread.start()
        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            log.info("Interrupted by user, exiting.")

    def __init__(
        self,
        target: Callable[..., None],
        name: str | None = None,
        priority: int = 0,
        stacks: Sequence[Layer] | None = None,
        data: Sequence[Any] | None = None,
    ) -> None:
        self.target = target
        self.name = name or _snake_to_camel(target.__name__)
        self.priority = priority
        self.stacks = (Plaintext(),) if stacks is None else stacks
        self.data = () if data is None else data


class Event:
    PEEK_TOKEN = "__peek__"  # noqa: S105

    def __init__(self, priority: int, token: str | None = None) -> None:
        self.priority = priority
        self.token = token
        self._event = threading.Event()

    def __repr__(self) -> str:
        return f"Event(priority={self.priority}, token={self.token})"

    def wait(self, timeout: float | None = None) -> None:
        if not self._event.wait(timeout):
            err_msg = f"Timed out after {timeout:g} seconds"
            raise TimeoutError(err_msg)

    def set(self) -> None:
        self._event.set()


class EventQueue:
    def __init__(self, name: str) -> None:
        self.name = name
        self._queue: list[Event] = []
        self._dummy = Event(0)
        self.token: str | None = None

    def __repr__(self) -> str:
        return f"EventQueue(name={self.name}, token={self.token}, queue={self._queue})"

    def __len__(self) -> int:
        return len(self._queue)

    def __bool__(self) -> bool:
        return len(self) > 0

    def _next(self) -> tuple[int, Event]:
        allowed_tokens = (self.token, Event.PEEK_TOKEN, None)
        queue = ((i, e) for i, e in enumerate(self._queue) if e.token in allowed_tokens)
        return max(queue, key=lambda e: e[1].priority, default=(0, self._dummy))

    def enqueue(
        self,
        priority: int = 0,
        token: str | None = None,
        timeout: float | None = None,
    ) -> None:
        event = Event(priority, token)
        log.debug("[%s] Enqueued: %s", self.name, event)
        self._queue.append(event)
        event.wait(timeout)

    def dequeue(self) -> None:
        i, event = self._next()
        if event is self._dummy:
            return
        log.debug("[%s] Dequeued: %s (%d)", self.name, event, i)
        if event.token != Event.PEEK_TOKEN:
            self.token = None
        del self._queue[i]
        event.set()

    def dequeue_all(self) -> None:
        while self._queue:
            self.dequeue()


class Medium:
    def __init__(self, interval: float = 1.0) -> None:
        self._msg: Message = Message.empty()
        self._interval = interval
        self._write_queue = EventQueue("Write")
        self._read_queue = EventQueue("Read")
        self._wait_queue = EventQueue("Wait")
        threading.Thread(target=self._tick, daemon=True).start()

    def _tick(self) -> None:
        for i in itertools.count(start=1):
            time.sleep(self._interval)
            log.debug("[Medium] Tick %d", i)
            if len(self._write_queue) and self._read_queue.token is None:
                self._write_queue.dequeue()
                time.sleep(self._interval)
            if not self._msg.is_empty:
                self._read_queue.dequeue()
            self._wait_queue.dequeue_all()

    def read(
        self,
        recipient: str | None,
        priority: int,
        *,
        timeout: float | None = None,
        clear: bool = True,
    ) -> Message:
        self._read_queue.enqueue(priority=priority, token=recipient, timeout=timeout)
        if clear:
            msg = self._msg
            self._msg = Message.empty()
        else:
            msg = self._msg.copy()
        return msg

    def write(self, msg: Message, priority: int, *, timeout: float | None = None) -> None:
        self._write_queue.enqueue(priority=priority, timeout=timeout)
        self._read_queue.token = msg.recipient
        self._msg = msg.copy()

    def wait(self, turns: int = 1) -> None:
        for _ in range(turns):
            self._wait_queue.enqueue()


class BytesAwareJSONEncoder(json.JSONEncoder):
    @classmethod
    def _decode_bytes(cls, obj: Body) -> Body:
        if isinstance(obj, dict):
            new_obj: dict[Any, Any] = {}
            for key, value in obj.items():
                if isinstance(value, bytes | bytearray):
                    new_obj[f"{key}_b64"] = base64.b64encode(value).decode("ascii")
                elif isinstance(value, str):
                    new_obj[key] = value
                else:
                    new_obj[key] = cls._decode_bytes(value)
            return new_obj
        if isinstance(obj, list):
            return [cls._decode_bytes(item) for item in obj]
        return obj

    def encode(self, o: Body) -> str:
        return super().encode(self._decode_bytes(o))


class BytesAwareJSONDecoder(json.JSONDecoder):
    @classmethod
    def _encode_bytes(cls, obj: Body) -> Body:
        if isinstance(obj, dict):
            new_obj: dict[Any, Any] = {}
            for key, value in obj.items():
                if key.endswith("_b64"):
                    new_obj[key[:-4]] = base64.b64decode(value)
                elif isinstance(value, str):
                    new_obj[key] = value
                else:
                    new_obj[key] = cls._encode_bytes(value)
            return new_obj
        if isinstance(obj, list):
            return [cls._encode_bytes(item) for item in obj]
        return obj

    def decode(self, s: str) -> Body:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._encode_bytes(super().decode(s))


def _from_json(data: ComplexBody) -> bytes | None:
    try:
        return json.dumps(data, cls=BytesAwareJSONEncoder).encode()
    except Exception:
        return None


def _to_json(data: bytes | bytearray) -> JSONBody | None:
    try:
        return json.loads(data, cls=BytesAwareJSONDecoder)
    except Exception:
        return None


def _from_utf8(data: str) -> bytes | None:
    try:
        return data.encode()
    except Exception:
        return None


def _to_utf8(data: bytes | bytearray) -> str | None:
    try:
        return data.decode()
    except Exception:
        return None


def _snake_to_camel(s: str) -> str:
    return "".join(word.capitalize() for word in s.split("_"))
