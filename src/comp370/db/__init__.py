"""
Database module for storing and querying Seinfeld episode data.

This module provides SQLAlchemy models and a database client for persisting
scraped Seinfeld data including seasons, episodes, writers, characters, and dialogue.
"""

from .models import (
    Base,
    Season,
    Writer,
    Episode,
    Character,
    Line,
)
from .client import Client

__all__ = ["Base", "Season", "Writer", "Episode", "Character", "Line", "Client"]
