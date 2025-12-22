# Implement an Attribute-Based Access Control (ABAC) scheme.
#
# - Assume that all users are already authenticated.
# - Users have the following attributes:
#   - "age" (int): the user's age.
#   - "paying" (bool): whether the user is a paying user.
# - Objects have the following attributes:
#   - "rating" (str): the movie's rating ("G", "PG-13", "R").
#   - "year" (int): the movie's release year.
# - The environment has the following attributes:
#   - "date" (datetime): the current date.
# - The following policies must be enforced:
#   - Rating policy: a user can watch a movie if they are old enough for its rating.
#                    (G: no restrictions, PG-13: 13+, R: 17+)
#   - Release policy: movies released in 2023 or later can only be watched by paying users,
#                     unless we are in a promotional period (between December 25 and December 31).
# - Make sure to implement fail-safe defaults for missing attributes.

import datetime
from collections.abc import Callable
from typing import Any

from issp import Actor, Channel, FileServer, Message, run_main

type Policy = Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], bool]

NEW_MOVIE_YEAR = 2023  # New movie release year.
RATINGS_AGE = {"G": 0, "PG-13": 13, "R": 17}  # Minimum ages for ratings.

DEFAULT_AGE = 0  # Default age for users.
DEFAULT_MOVIE_YEAR = NEW_MOVIE_YEAR  # Default year for movies.
DEFAULT_RATING = "R"  # Default rating for movies.


class Server(FileServer):
    def __init__(self, name: str, channels: Channel | dict[str, Channel]) -> None:
        super().__init__(name, channels)

        self.files = {
            "toy_story.mov": "This is a G-rated old movie.",
            "elemental.mov": "This is a G-rated new movie.",
            "interstellar.mov": "This is a PG-13-rated old movie.",
            "dune_2.mov": "This is a PG-13-rated new movie.",
            "ex_machina.mov": "This is an R-rated old movie.",
            "oppenheimer.mov": "This is an R-rated new movie.",
        }

        self.subj: dict[str, dict[str, Any]] = {
            "Bob": {"paying": True},
            "Carl": {"age": 14, "paying": False},
            "Diana": {"age": 15, "paying": True},
            "Evan": {"age": 18},
            "Frank": {"age": 25, "paying": True},
        }

        self.obj: dict[str, dict[str, Any]] = {
            "toy_story.mov": {"rating": "G", "year": 1995},
            "elemental.mov": {"rating": "G"},
            "interstellar.mov": {"rating": "PG-13", "year": 2014},
            "dune_2.mov": {"rating": "PG-13", "year": 2024},
            "ex_machina.mov": {"year": 2014},
            "oppenheimer.mov": {"rating": "R", "year": 2023},
        }

        self.env = {
            "date": datetime.datetime.now(tz=datetime.UTC),
        }

        def rating_policy(s: dict[str, Any], o: dict[str, Any], e: dict[str, Any]) -> bool:
            return s.get("age", DEFAULT_AGE) >= RATINGS_AGE[o.get("rating", DEFAULT_RATING)]

        def paying_rule(s: dict[str, Any], o: dict[str, Any], e: dict[str, Any]) -> bool:
            return o.get("year", DEFAULT_MOVIE_YEAR) < NEW_MOVIE_YEAR or s.get("paying", False)

        def promo_rule(s: dict[str, Any], o: dict[str, Any], e: dict[str, Any]) -> bool:
            date: datetime.datetime = e["date"]
            return date.month == 12 and 25 <= date.day <= 31

        def release_policy(s: dict[str, Any], o: dict[str, Any], e: dict[str, Any]) -> bool:
            return paying_rule(s, o, e) or promo_rule(s, o, e)

        self.policies = {
            "read": [rating_policy, release_policy],
        }

    def authorize(self, sender: str, body: dict[str, Any]) -> bool:
        # Reject unknown actions.
        if (policies := self.policies.get(body["action"])) is None:
            return False

        # Allow access only if all policies for the action are satisfied.
        subj = self.subj.get(sender, {})
        obj = self.obj.get(body["path"], {})
        return all(policy(subj, obj, self.env) for policy in policies)


def server(channel: Channel) -> None:
    Server("Server", channel).listen()


def watch_all(actor: str, channel: Channel) -> None:
    movies = (
        "toy_story.mov",
        "elemental.mov",
        "interstellar.mov",
        "dune_2.mov",
        "ex_machina.mov",
        "oppenheimer.mov",
    )

    for path in movies:
        msg = {"action": "read", "path": path}
        channel.request(Message(actor, "Server", msg), quiet=True)


def alice(channel: Channel) -> None:
    watch_all("Alice", channel)


def bob(channel: Channel) -> None:
    watch_all("Bob", channel)


def carl(channel: Channel) -> None:
    watch_all("Carl", channel)


def diana(channel: Channel) -> None:
    watch_all("Diana", channel)


def evan(channel: Channel) -> None:
    watch_all("Evan", channel)


def frank(channel: Channel) -> None:
    watch_all("Frank", channel)


def main() -> None:
    Actor.start(
        Actor(server, priority=7),
        Actor(alice, priority=6),
        Actor(bob, priority=5),
        Actor(carl, priority=4),
        Actor(diana, priority=3),
        Actor(evan, priority=2),
        Actor(frank, priority=1),
    )


if __name__ == "__main__":
    run_main(main)
