"""
Data models for scraped Seinfeld episode information.

These dataclasses represent the structured data extracted from IMSDB,
including season organization, episode metadata, and parsed scripts.
"""

from datetime import date
from dataclasses import dataclass


@dataclass
class Season:
    """
    Represents a season of Seinfeld.

    Attributes:
        number: The season number
        episodes: List of episode titles in this season
    """

    number: int
    episodes: list[str]


@dataclass
class Episode:
    """
    Represents metadata for a Seinfeld episode.

    Attributes:
        title: The episode title
        writers: List of writer names who wrote this episode
        air_date: The original air date of the episode
    """

    title: str
    writers: list[str]
    air_date: date


@dataclass
class Script:
    """
    Represents a parsed Seinfeld script.

    Attributes:
        lines: List of (character, dialogue) tuples representing
               each line of dialogue in the script
    """

    lines: list[tuple[str, str]]
