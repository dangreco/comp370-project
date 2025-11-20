"""
SQLAlchemy ORM models for Seinfeld episode data.

This module defines the database schema for storing seasons, episodes,
writers, characters, and dialogue lines with their relationships.
"""

from __future__ import annotations
import datetime
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


# Association table for many-to-many relationship between episodes and writers
episode_writer_link = Table(
    "episode_writer_link",
    Base.metadata,
    Column("episode_id", Integer, ForeignKey("episode.id"), primary_key=True),
    Column("writer_id", Integer, ForeignKey("person.id"), primary_key=True),
)

# Association table for many-to-many relationship between episodes and characters
episode_character_link = Table(
    "episode_character_link",
    Base.metadata,
    Column("episode_id", Integer, ForeignKey("episode.id"), primary_key=True),
    Column("character_id", Integer, ForeignKey("character.id"), primary_key=True),
)

# Association table for many-to-many relationship between persons and characters
person_character_link = Table(
    "person_character_link",
    Base.metadata,
    Column("person_id", Integer, ForeignKey("person.id"), primary_key=True),
    Column("character_id", Integer, ForeignKey("character.id"), primary_key=True),
)


class Season(Base):
    """
    Represents a season of Seinfeld.

    Attributes:
        id: Primary key
        number: Season number (1-9)
        episodes: List of episodes in this season
    """

    __tablename__ = "season"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(nullable=False)

    episodes: Mapped[List["Episode"]] = relationship(
        back_populates="season",
        cascade="all, delete-orphan",
    )


class Episode(Base):
    """
    Represents an episode of Seinfeld.

    Attributes:
        id: Primary key
        number: Episode number within the season
        title: Episode title (e.g., "The Pilot")
        air_date: Original air date
        season_id: Foreign key to Season
        season: The season this episode belongs to
        writers: List of writers who wrote this episode
        characters: List of characters who appear in this episode
        lines: All dialogue lines in this episode (ordered by line number)
    """

    __tablename__ = "episode"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[datetime.date] = mapped_column(nullable=False)

    season: Mapped["Season"] = relationship(back_populates="episodes")
    season_id: Mapped[int] = mapped_column(
        ForeignKey("season.id"),
        nullable=False,
    )

    writers: Mapped[List["Person"]] = relationship(
        secondary="episode_writer_link",
        back_populates="written",
    )

    characters: Mapped[List["Character"]] = relationship(
        secondary="episode_character_link",
        back_populates="episodes",
    )

    lines: Mapped[List["Line"]] = relationship(
        back_populates="episode",
        cascade="all, delete-orphan",
        order_by="Line.number",
    )


class Person(Base):
    """
    Represents a person who worked on Seinfeld episodes.

    Attributes:
        id: Primary key
        name: Person's name
        written: List of episodes this person wrote
        characters: List of characters this person acted as
    """

    __tablename__ = "person"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    written: Mapped[List["Episode"]] = relationship(
        secondary="episode_writer_link",
        back_populates="writers",
    )

    characters: Mapped[List["Character"]] = relationship(
        secondary="person_character_link",
        back_populates="actors",
    )


class Character(Base):
    """
    Represents a character in Seinfeld.

    Attributes:
        id: Primary key
        name: Character name (e.g., "Jerry Seinfeld")
        gender: Character gender (e.g., "male", "female")
        occupation: Character occupation (e.g., "comedian", "actor")
        episodes: List of episodes this character appears in
        lines: All dialogue lines spoken by this character
        actors: List of actors who played this character
    """

    __tablename__ = "character"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    gender: Mapped[str] = mapped_column(nullable=False)
    occupation: Mapped[str] = mapped_column(nullable=False)

    episodes: Mapped[List["Episode"]] = relationship(
        secondary="episode_character_link",
        back_populates="characters",
    )

    actors: Mapped[List["Person"]] = relationship(
        secondary="person_character_link",
        back_populates="characters",
    )

    lines: Mapped[List["Line"]] = relationship(
        back_populates="character",
        cascade="all, delete-orphan",
    )


class Line(Base):
    """
    Represents a single line of dialogue in a Seinfeld episode.

    Attributes:
        id: Primary key
        number: Line number within the episode (sequential)
        dialogue: The dialogue text
        episode_id: Foreign key to Episode
        episode: The episode this line is from
        character_id: Foreign key to Character
        character: The character who speaks this line
    """

    __tablename__ = "line"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(nullable=False)
    dialogue: Mapped[str] = mapped_column(nullable=False)

    episode: Mapped["Episode"] = relationship(back_populates="lines")
    episode_id: Mapped[int] = mapped_column(
        ForeignKey("episode.id"),
        nullable=False,
    )

    character: Mapped["Character"] = relationship(back_populates="lines")
    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id"),
        nullable=False,
    )
