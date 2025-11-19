"""
GraphQL schema definitions for Seinfeld episode data.

This module defines GraphQL types and queries using Graphene and
graphene-sqlalchemy to expose the database models through a GraphQL API.
"""

import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy import SQLAlchemyConnectionField

from comp370.db.models import Season, Episode, Writer, Character, Line


class SeasonType(SQLAlchemyObjectType):
    """GraphQL type for Season model with Relay support."""

    class Meta:
        model = Season
        interfaces = (relay.Node,)


class EpisodeType(SQLAlchemyObjectType):
    """GraphQL type for Episode model with Relay support."""

    class Meta:
        model = Episode
        interfaces = (relay.Node,)


class WriterType(SQLAlchemyObjectType):
    """GraphQL type for Writer model with Relay support."""

    class Meta:
        model = Writer
        interfaces = (relay.Node,)


class LineType(SQLAlchemyObjectType):
    """GraphQL type for Line model with Relay support."""

    class Meta:
        model = Line
        interfaces = (relay.Node,)


class CharacterType(SQLAlchemyObjectType):
    """GraphQL type for Character model with Relay support."""

    class Meta:
        model = Character
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    """
    Root GraphQL query type.

    Provides both collection queries (all_*) with pagination support
    and individual item queries (season, episode, character).
    """

    # Collection queries with Relay pagination
    all_seasons = SQLAlchemyConnectionField(SeasonType.connection)
    all_episodes = SQLAlchemyConnectionField(EpisodeType.connection)
    all_writers = SQLAlchemyConnectionField(WriterType.connection)
    all_characters = SQLAlchemyConnectionField(CharacterType.connection)
    all_lines = SQLAlchemyConnectionField(LineType.connection)

    # Individual item queries
    season = graphene.Field(
        SeasonType,
        number=graphene.Int(required=True),
        description="Get a specific season by number",
    )

    episode = graphene.Field(
        EpisodeType,
        season=graphene.Int(required=True),
        number=graphene.Int(required=True),
        description="Get a specific episode by season and episode number",
    )

    character = graphene.Field(
        CharacterType,
        name=graphene.String(required=True),
        description="Get a specific character by name",
    )

    def resolve_season(self, info, number):
        """Resolve a season by its number."""
        session = info.context["session"]
        return session.query(Season).filter(Season.number == number).first()

    def resolve_episode(self, info, season, number):
        """Resolve an episode by season and episode number."""
        session = info.context["session"]
        return (
            session.query(Episode)
            .join(Episode.season)
            .filter(Season.number == season, Episode.number == number)
            .first()
        )

    def resolve_character(self, info, name):
        """Resolve a character by name."""
        session = info.context["session"]
        return session.query(Character).filter(Character.name == name).first()


# Main GraphQL schema
schema = graphene.Schema(query=Query)
