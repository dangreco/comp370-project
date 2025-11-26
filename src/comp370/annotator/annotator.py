from abc import ABC
from abc import abstractmethod
from typing import TypeVar
from typing import Generic
from typing import Optional
from sqlalchemy.orm import joinedload

from comp370.db.models import Line
from comp370.db.client import Client as Db
from .codebook import Codebook

Engine = TypeVar("Engine")


class Annotator(ABC, Generic[Engine]):
    def __init__(self, engine: Engine, codebook: Optional[Codebook] = None) -> None:
        self.engine = engine
        self.codebook = codebook

    def context(self, line: Line, n: int = 1) -> list[Line]:
        """Retrieve n lines of context before the given line."""
        with Db().session() as db:
            context_lines = (
                db.query(Line)
                .join(Line.character)
                .options(joinedload(Line.character))  # Eager load the character
                .filter(Line.episode_id == line.episode_id)
                .filter(Line.number < line.number)
                .order_by(Line.number.desc())
                .limit(n)
                .all()
            )
            context_lines.reverse()
            return context_lines

    @abstractmethod
    def annotate(self, line: Line, max_attempts: int = 1) -> str:
        """Annotate a line of dialogue and return the annotation as a string."""
        pass

    @abstractmethod
    def models(self) -> list[str]:
        """Return a list of available models for the annotator."""
        pass
