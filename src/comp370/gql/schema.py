"""
GraphQL schema definitions for Seinfeld episode data.

This module defines GraphQL types and queries using Graphene and
graphene-sqlalchemy to expose the database models through a GraphQL API.
"""

import random
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy import SQLAlchemyConnectionField
from sqlalchemy import func
from typing import Any

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


def _resolve_random(
    typ: Any,
    info,
    n,
    replace=False,
):
    session = info.context["session"]

    # Query IDs
    ids = [sid for (sid,) in session.query(typ.id).all()]
    total = len(ids)

    if total == 0:
        return []

    if replace:
        sampled = [random.choice(ids) for _ in range(n)]
        return session.query(typ).filter(typ.id.in_(sampled)).all()

    if n >= total:
        random.shuffle(ids)
        return session.query(typ).filter(typ.id.in_(ids)).all()

    sampled = random.sample(ids, n)
    return session.query(typ).filter(typ.id.in_(sampled)).all()


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

    # Random sample queries
    random_seasons = graphene.List(
        SeasonType,
        n=graphene.Int(required=True),
        replace=graphene.Boolean(required=False, default_value=False),
        description="Get a random sample of seasons",
    )

    random_episodes = graphene.List(
        EpisodeType,
        n=graphene.Int(required=True),
        replace=graphene.Boolean(required=False, default_value=False),
        description="Get a random sample of episodes",
    )

    random_characters = graphene.List(
        CharacterType,
        n=graphene.Int(required=True),
        replace=graphene.Boolean(required=False, default_value=False),
        description="Get a random sample of characters",
    )

    random_lines = graphene.List(
        LineType,
        n=graphene.Int(required=True),
        replace=graphene.Boolean(required=False, default_value=False),
        min_length=graphene.Int(required=False, default_value=None),
        max_length=graphene.Int(required=False, default_value=None),
        character_id=graphene.ID(required=False, default_value=None),
        description="Get a random sample of lines",
    )

    def resolve_random_seasons(self, info, n, replace=False):
        """Resolve a random sample of seasons."""
        return _resolve_random(Season, info, n, replace)

    def resolve_random_episodes(self, info, n, replace=False):
        """Resolve a random sample of episodes."""
        return _resolve_random(Episode, info, n, replace)

    def resolve_random_characters(self, info, n, replace=False):
        """Resolve a random sample of characters."""
        return _resolve_random(Character, info, n, replace)

    def resolve_random_lines(
        self,
        info,
        n,
        replace=False,
        min_length=None,
        max_length=None,
        character_id=None,
    ):
        """Resolve a random sample of lines."""
        session = info.context["session"]

        if character_id is not None:
            character = relay.Node.get_node_from_global_id(info, character_id)
            character_db_id = character.id

        # Query IDs
        query = session.query(Line)

        if min_length is not None:
            query = query.filter(func.length(Line.dialogue) >= min_length)

        if max_length is not None:
            query = query.filter(func.length(Line.dialogue) <= max_length)

        if character_db_id is not None:
            query = query.filter(Line.character_id == character_db_id)

        # Get filtered IDs
        ids = [sid for (sid,) in query.with_entities(Line.id).all()]
        total = len(ids)

        if total == 0:
            return []

        if replace:
            sampled = [random.choice(ids) for _ in range(n)]
            return session.query(Line).filter(Line.id.in_(sampled)).all()

        if n >= total:
            random.shuffle(ids)
            return session.query(Line).filter(Line.id.in_(ids)).all()

        sampled = random.sample(ids, n)
        return session.query(Line).filter(Line.id.in_(sampled)).all()


# Main GraphQL schema
schema = graphene.Schema(query=Query)
