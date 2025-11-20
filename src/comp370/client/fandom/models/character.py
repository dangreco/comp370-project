from dataclasses import dataclass
from typing import Optional


@dataclass
class Character:
    path: str
    name: str
    gender: str
    occupation: str
    portrayed_by: list[str]
    episode: Optional[str]
