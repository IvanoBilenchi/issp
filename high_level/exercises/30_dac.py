# Implement a Discretionary Access Control (DAC) scheme.
#
# - Assume that all users are already authenticated.
# - The scheme should support the concept of file ownership.
# - The owner of a file implicitly has read and write permissions, and can grant
#   (and revoke) read and write access to other users.
# - Alice, Bob, and Carl are the owners of files "file_a.txt", "file_b.txt",
#   and "file_c.txt", respectively.
# - Make sure to implement fail-safe defaults.

from typing import Any

from issp import Actor, Channel, FileServer, Message, run_main

DEFAULT_ACL: dict[str, set[str]] = {}  # Empty ACL
DEFAULT_PERMISSIONS: set[str] = set()  # No permissions
ASSIGNABLE_PERMISSIONS = {"read", "write"}  # Permissions that can be assigned


class Server(FileServer):
    def __init__(self, name: str, channels: Channel | dict[str, Channel]) -> None:
        super().__init__(name, channels)
        self.add_handler("set_permissions", self.set_permissions)

        self.files = {
            "file_a.txt": "This file belongs to Alice.",
            "file_b.txt": "This file belongs to Bob.",
            "file_c.txt": "This file belongs to Carl.",
        }

        # TO-DO: Add any necessary data structures.

    def authorize(self, sender: str, body: dict[str, Any]) -> bool:
        # TO-DO: Implement the authorization logic.
        return False

    def set_permissions(self, sender: str, body: dict[str, Any]) -> dict[str, Any]:
        # TO-DO: Implement the permission setting logic.
        return {"status": "error"}


def server(channel: Channel) -> None:
    Server("Server", channel).listen()


def write_read_all(actor: str, channel: Channel) -> None:
    files = ("file_a.txt", "file_b.txt", "file_c.txt")

    for path in files:
        msg = {"action": "write", "path": path, "data": f" Written by {actor}."}
        channel.request(Message(actor, "Server", msg), quiet=True)

    for path in files:
        msg = {"action": "read", "path": path}
        channel.request(Message(actor, "Server", msg), quiet=True)


def alice(channel: Channel) -> None:
    write_read_all("Alice", channel)

    for path in ("file_a.txt", "file_b.txt", "file_c.txt"):
        msg = {
            "action": "set_permissions",
            "path": path,
            "target": "Bob",
            "permissions": ["write"],
        }
        channel.request(Message("Alice", "Server", msg), quiet=True)

    for path in ("file_a.txt", "file_b.txt", "file_c.txt"):
        msg = {
            "action": "set_permissions",
            "path": path,
            "target": "Carl",
            "permissions": ["read"],
        }
        channel.request(Message("Alice", "Server", msg), quiet=True)


def bob(channel: Channel) -> None:
    write_read_all("Bob", channel)


def carl(channel: Channel) -> None:
    write_read_all("Carl", channel)


def main() -> None:
    Actor.start(
        Actor(server, priority=4),
        Actor(alice, priority=3),
        Actor(bob, priority=2),
        Actor(carl, priority=1),
    )


if __name__ == "__main__":
    run_main(main)
