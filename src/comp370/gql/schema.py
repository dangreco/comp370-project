"""
GraphQL schema definitions for Seinfeld episode data.

This module defines GraphQL types and queries using Graphene and
graphene-sqlalchemy to expose the database models through a GraphQL API.
"""

import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy import SQLAlchemyConnectionField

from comp370.db.models import Season, Episode, Person, Character, Line


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


class PersonType(SQLAlchemyObjectType):
    """GraphQL type for Person model with Relay support."""

    class Meta:
        model = Person
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
    seasons = SQLAlchemyConnectionField(SeasonType.connection)
    episodes = SQLAlchemyConnectionField(EpisodeType.connection)
    people = SQLAlchemyConnectionField(PersonType.connection)
    characters = SQLAlchemyConnectionField(CharacterType.connection)
    lines = SQLAlchemyConnectionField(LineType.connection)

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

    person = graphene.Field(
        PersonType,
        name=graphene.String(required=True),
        description="Get a specific person by name",
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

    def resolve_person(self, info, name):
        """Resolve a person by name."""
        session = info.context["session"]
        return session.query(Person).filter(Person.name == name).first()

    def resolve_character(self, info, name):
        """Resolve a character by name."""
        session = info.context["session"]
        return session.query(Character).filter(Character.name == name).first()


# Main GraphQL schema
schema = graphene.Schema(query=Query)
