# Implement a Mandatory Access Control (MAC) scheme based on the Bell-LaPadula model.
#
# - Assume that all users are already authenticated.
# - Alice, Bob, and Carl have different security clearances. Bob has clearance
#   for confidential files, Carl for secret files, while Alice does not have an explicit clearance.
# - You must implement the ss-property and the *-property.
# - Make sure to implement fail-safe defaults.
#
# Hints:
# - Authorization decisions should be based on the "action" and "path" fields in the message body.
# - To avoid clutter, access control exercises only log activities as seen from the server side.

from typing import Any

from issp import Actor, Channel, FileServer, Message, run_main

DEFAULT_LABEL = 2  # Secret
DEFAULT_CLEARANCE = 0  # Unclassified


class Server(FileServer):
    def __init__(self, name: str, channels: Channel | dict[str, Channel]) -> None:
        super().__init__(name, channels)

        self.files = {
            "public.txt": "This is a public file.",
            "confidential.txt": "This is a confidential file.",
            "secret.txt": "This is a secret file.",
        }

        # TO-DO: Add any necessary data structures.

    def authorize(self, sender: str, body: dict[str, Any]) -> bool:
        # TO-DO: Implement the authorization logic.
        return False


def server(channel: Channel) -> None:
    Server("Server", channel).listen()


def write_read_all(actor: str, channel: Channel) -> None:
    files = ("public.txt", "confidential.txt", "secret.txt")

    for path in files:
        msg = {"action": "write", "path": path, "data": f" Written by {actor}."}
        channel.request(Message(actor, "Server", msg), quiet=True)

    for path in files:
        msg = {"action": "read", "path": path}
        channel.request(Message(actor, "Server", msg), quiet=True)


def alice(channel: Channel) -> None:
    write_read_all("Alice", channel)


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
