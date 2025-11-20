"""
Database client for managing SQLAlchemy connections and sessions.

This module provides a Client class that handles database initialization,
connections, and session management for the Seinfeld data.
"""

from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from comp370.constants import DIR_DATA
from .constants import SQLITE_DATABASE
from .models import Base, Season, Episode, Person, Character, Line  # noqa: F401


class Client:
    """
    Database client for managing SQLite connections and sessions.

    This client handles database initialization, creates tables if they
    don't exist, and provides session management for database operations.

    Attributes:
        path: Path to the SQLite database file
        database: Name of the database
        engine: SQLAlchemy engine instance (None until connected)
    """

    path: Path
    database: str
    engine: Optional[Engine]

    def __init__(
        self,
        path: Path = DIR_DATA / f"{SQLITE_DATABASE}.db",
        database: str = SQLITE_DATABASE,
    ):
        """
        Initialize the database client.

        Args:
            path: Path where the SQLite database file will be stored.
                 Defaults to DIR_DATA/comp370.db
            database: Name of the database. Defaults to "comp370"
        """
        self.path = path
        self.database = database
        self.engine = None

    def connect(self):
        """
        Establish database connection and create tables.

        Creates a SQLAlchemy engine and initializes all tables defined
        in the models if they don't already exist. This method is
        idempotent - calling it multiple times has no effect after
        the first call.
        """
        if self.engine is not None:
            return
        self.engine = create_engine(f"sqlite:///{self.path}")
        Base.metadata.create_all(self.engine)

    def session(self):
        """
        Create and return a new database session.

        Automatically connects to the database if not already connected.

        Returns:
            A new SQLAlchemy Session instance for database operations
        """
        if self.engine is None:
            self.connect()
        return Session(self.engine, future=True)
