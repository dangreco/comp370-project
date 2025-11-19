"""
GraphQL API module for querying Seinfeld episode data.

This module provides a Graphene-based GraphQL schema for querying
seasons, episodes, writers, characters, and dialogue lines.
"""

from .schema import schema, SeasonType, EpisodeType, PersonType, CharacterType, LineType

__all__ = [
    "schema",
    "SeasonType",
    "EpisodeType",
    "PersonType",
    "CharacterType",
    "LineType",
]
