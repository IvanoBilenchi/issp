# Implement a basic Role-Based Access Control (RBAC) scheme.
#
# - Assume that all users are already authenticated.
# - The scheme should support the concept of roles, role assignments, and sessions.
# - Users may have multiple roles.
# - No explicit access rights are required to start and end sessions: anyone can do it.
# - Roles are as follows:
#   - "reader" can read the log file.
#   - "writer" can write to the log file.
#   - "admin" can assign and unassign any role.
# - Initial role assignments are as follows:
#   - Admin: admin, writer, reader
#   - Service: writer
# - Make sure to implement fail-safe defaults.

from typing import Any

from issp import Actor, Channel, FileServer, Message, run_main

DEFAULT_ASSIGNMENTS: set[str] = set()  # No roles assigned
DEFAULT_SESSION: set[str] = set()  # No active roles


class Server(FileServer):
    def __init__(self, name: str, channels: Channel | dict[str, Channel]) -> None:
        super().__init__(name, channels)
        self.add_handler("start_session", self.start_session)
        self.add_handler("end_session", self.end_session)
        self.add_handler("add_role", self.add_role)
        self.add_handler("remove_role", self.remove_role)

        self.files = {"log.txt": "This is the log file."}

        # TO-DO: Add any necessary data structures.

    def authorize(self, sender: str, body: dict[str, Any]) -> bool:
        # TO-DO: Implement the authorization logic.
        return False

    def start_session(self, sender: str, body: dict[str, Any]) -> dict[str, Any]:
        # TO-DO: Implement session creation, making sure the user can only
        #        request roles they have been assigned.
        return {"status": "error"}

    def end_session(self, sender: str, body: dict[str, Any]) -> dict[str, Any]:
        # TO-DO: Implement session termination.
        return {"status": "error"}

    def add_role(self, sender: str, body: dict[str, Any]) -> dict[str, Any]:
        # TO-DO: Implement role assignment.
        return {"status": "error"}

    def remove_role(self, sender: str, body: dict[str, Any]) -> dict[str, Any]:
        # TO-DO: Implement role unassignment.
        return {"status": "error"}


def server(channel: Channel) -> None:
    Server("Server", channel).listen()


def admin(channel: Channel) -> None:
    # No session active, operations should fail.
    msg = {"action": "write", "path": "log.txt", "data": " Written by Admin."}
    channel.request(Message("Admin", "Server", msg), quiet=True)

    msg = {"action": "read", "path": "log.txt"}
    channel.request(Message("Admin", "Server", msg), quiet=True)

    msg = {"action": "add_role", "target": "Service", "role": "writer"}
    channel.request(Message("Admin", "Server", msg), quiet=True)

    # Start a session with "admin" role.
    msg = {"action": "start_session", "roles": ["admin"]}
    channel.request(Message("Admin", "Server", msg), quiet=True)

    # Provide Service with the "reader" role.
    channel.wait_for("Service")
    msg = {"action": "add_role", "target": "Service", "role": "reader"}
    channel.request(Message("Admin", "Server", msg), quiet=True)


def service(channel: Channel) -> None:
    # Trying to start a session with "reader" role, which is not assigned.
    msg = {"action": "start_session", "roles": ["reader"]}
    channel.request(Message("Service", "Server", msg), quiet=True)

    # Trying to start a session with "reader" role, which is now assigned.
    msg = {"action": "start_session", "roles": ["reader"]}
    channel.request(Message("Service", "Server", msg), quiet=True)

    # Write operation should fail.
    msg = {"action": "write", "path": "log.txt", "data": " Written by Service."}
    channel.request(Message("Service", "Server", msg), quiet=True)

    # Read operation should succeed.
    msg = {"action": "read", "path": "log.txt"}
    channel.request(Message("Service", "Server", msg), quiet=True)


def main() -> None:
    Actor.start(Actor(server, priority=3), Actor(admin, priority=2), Actor(service, priority=1))


if __name__ == "__main__":
    run_main(main)
