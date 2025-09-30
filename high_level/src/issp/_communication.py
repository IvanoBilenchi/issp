from __future__ import annotations

import base64
import heapq
import itertools
import json
import sys
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from . import _log as log
from ._util import snake_to_camel

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any


type JSONBody = ComplexBody | str
type ComplexBody = dict[Any, Any] | list[Any]
type SimpleBody = bytes | str
type Body = ComplexBody | SimpleBody


class Message:
    @staticmethod
    def encode_body(body: Body) -> bytes:
        if isinstance(body, bytes):
            return body
        if isinstance(body, str) and (data := _from_utf8(body)):
            return data
        if isinstance(body, (dict, list)) and (data := _from_json(body)):
            return data
        return str(body).encode()

    @staticmethod
    def decode_body(data: bytes) -> Body:
        if body := _to_json(data):
            return body
        if body := _to_utf8(data):
            return body
        return data

    @classmethod
    def empty(cls) -> Message:
        return cls("", "", b"")

    def __init__(self, sender: str, recipient: str, body: Body) -> None:
        self.sender = sender
        self.recipient = recipient
        self.body = self.encode_body(body)

    def __repr__(self) -> str:
        body = self.decode_body(self.body)
        return f"Message(from={self.sender!r}, to={self.recipient!r}, body={body!r})"


@dataclass(order=True)
class Event:
    priority: int
    event: threading.Event = field(compare=False)


class EventQueue:
    def __init__(self) -> None:
        self._queue: list[Event] = []

    def __len__(self) -> int:
        return len(self._queue)

    def __bool__(self) -> bool:
        return len(self) > 0

    def enqueue(self, priority: int = 0) -> None:
        event = threading.Event()
        heapq.heappush(self._queue, Event(-priority, event))
        event.wait()

    def dequeue(self) -> None:
        if self._queue:
            heapq.heappop(self._queue).event.set()

    def dequeue_all(self) -> None:
        while self._queue:
            heapq.heappop(self._queue).event.set()


class AccessQueue:
    def __init__(self, interval: float = 1.0) -> None:
        self._interval = interval
        self._send_queue = EventQueue()
        self._rcv_queue = EventQueue()
        self._wait_queue = EventQueue()
        threading.Thread(target=self._tick, daemon=True).start()

    def _tick(self) -> None:
        for i in itertools.count(start=1):
            time.sleep(self._interval)
            log.debug("[Queue] Slot %d", i)
            should_wait_again = len(self._send_queue) > 0
            self._send_queue.dequeue()
            if should_wait_again:
                time.sleep(self._interval)
            self._rcv_queue.dequeue()
            self._wait_queue.dequeue_all()

    def request_send(self, priority: int = 0) -> None:
        self._send_queue.enqueue(priority)

    def give_up_send(self) -> None:
        self._send_queue.dequeue()

    def request_receive(self, priority: int = 0) -> None:
        self._rcv_queue.enqueue(priority)

    def give_up_receive(self) -> None:
        self._rcv_queue.dequeue()

    def wait(self, turns: int = 1) -> None:
        for _ in range(turns):
            self._wait_queue.enqueue()


class Channel:
    def __init__(self, stack: Layer, access_queue: AccessQueue) -> None:
        self.stack = stack
        self._access_queue = access_queue

    def send(self, msg: Message, *, priority: int = 0) -> None:
        self._access_queue.request_send(priority=priority)
        self.stack.write(msg)

    def receive(self, recipient: str, *, priority: int = 0) -> Message:
        self._access_queue.request_receive(priority=priority)
        if (msg := self.stack[-1].read()) and msg.recipient == recipient:
            return self.stack.read()
        self._access_queue.give_up_receive()
        return self.receive(recipient, priority=priority)

    def peek(self) -> Message:
        self._access_queue.request_receive(priority=sys.maxsize)
        return self.stack.read()

    def wait(self, turns: int = 1) -> None:
        self._access_queue.wait(turns)

    def with_stack(self, stack: Layer, *, keep_log_top: bool = True) -> Channel:
        stack = stack | self.stack[-1]
        if keep_log_top and isinstance(self.stack, LoggingLayer):
            stack = LoggingLayer(self.stack.tag) | stack
        return Channel(stack, self._access_queue)


class Layer:
    def __init__(self) -> None:
        self.lower_layer: Layer | None = None

    def __or__(self, base: object) -> Layer:
        if not isinstance(base, Layer):
            err_msg = f"Unsupported operand type(s) for |: '{type(self)}' and '{type(base)}'"
            raise TypeError(err_msg)
        self.lower_layer = base
        return self

    def __len__(self) -> int:
        return 1 + (len(self.lower_layer) if self.lower_layer else 0)

    def __getitem__(self, index: int) -> Layer:
        if index == 0:
            return self
        if index < 0:
            index = len(self) + index
        if self.lower_layer is None:
            msg = "Layer index out of range"
            raise IndexError(msg)
        return self.lower_layer[index - 1]

    def write(self, msg: Message) -> None:
        if self.lower_layer is None:
            err_msg = "Physical layer not found"
            raise ValueError(err_msg)
        self.lower_layer.write(msg)

    def read(self) -> Message:
        if self.lower_layer is None:
            err_msg = "Physical layer not found"
            raise ValueError(err_msg)
        return self.lower_layer.read()


class PhysicalLayer(Layer):
    def __init__(self) -> None:
        super().__init__()
        self._msg = Message.empty()

    def __or__(self, base: object) -> Layer:
        del base  # unused
        err_msg = "You've hit rock bottom, my friend"
        raise TypeError(err_msg)

    def write(self, msg: Message) -> None:
        self._msg = msg

    def read(self) -> Message:
        return self._msg


class LoggingLayer(Layer):
    def __init__(self, tag: str = "") -> None:
        super().__init__()
        self.tag = tag

    def _format_tag(self) -> str:
        return f"[{self.tag}] " if self.tag else ""

    def write(self, msg: Message) -> None:
        log.info("%sSent: %s", self._format_tag(), msg)
        super().write(msg)

    def read(self) -> Message:
        msg = super().read()
        log.info("%sReceived: %s", self._format_tag(), msg)
        return msg


class Actor:
    def __init__(
        self,
        target: Callable[..., None],
        name: str | None = None,
        stacks: Sequence[Layer] = (),
        data: Sequence[Any] = (),
    ) -> None:
        self.target = target
        self.name = name or snake_to_camel(target.__name__)
        self.stacks = stacks
        self.data = data


def start_actors(*args: Callable[[Channel], None] | Actor, interval: float = 1.0) -> None:
    phys = PhysicalLayer()
    queue = AccessQueue(interval=interval)
    for arg in args:
        actor = Actor(arg) if isinstance(arg, Callable) else arg
        stacks = (s | phys for s in actor.stacks)
        stacks = (LoggingLayer(tag=actor.name) | s for s in (phys, *stacks))
        channels = tuple(Channel(s, queue) for s in stacks)
        threading.Thread(target=actor.target, args=(*channels, *actor.data)).start()


class BytesAwareJSONEncoder(json.JSONEncoder):
    @classmethod
    def _decode_bytes(cls, obj: Body) -> Body:
        if isinstance(obj, dict):
            new_obj: dict[Any, Any] = {}
            for key, value in obj.items():
                if isinstance(value, bytes):
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
                if isinstance(key, str) and key.endswith("_b64"):
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


def _to_json(data: bytes) -> Body | None:
    try:
        return json.loads(data, cls=BytesAwareJSONDecoder)
    except Exception:
        return None


def _from_utf8(data: str) -> bytes | None:
    try:
        return data.encode()
    except Exception:
        return None


def _to_utf8(data: bytes) -> str | None:
    try:
        return data.decode()
    except Exception:
        return None
