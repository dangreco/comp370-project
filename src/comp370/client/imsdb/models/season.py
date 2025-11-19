from dataclasses import dataclass

from .episode import Episode


@dataclass
class Season:
    number: int
    episodes: list[Episode]
