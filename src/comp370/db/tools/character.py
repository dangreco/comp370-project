from enum import Enum
from typing import Optional
from sqlalchemy import func

from comp370.db.models import Character
from comp370.db.models import Episode
from comp370.db.models import Line
from .tool import Tool


THRESH_MAIN = 0.700
THRESH_SIDE = 0.100
THRESH_RECURRING = 0.005
assert 0 < THRESH_RECURRING < THRESH_SIDE < THRESH_MAIN < 1


class CharacterType(Enum):
    MAIN = "main"
    SIDE = "side"
    RECURRING = "recurring"
    GUEST = "guest"

    @staticmethod
    def classify(n: int, total: int) -> "CharacterType":
        ratio = n / total if total > 0 else 0
        if ratio >= THRESH_MAIN:
            return CharacterType.MAIN
        elif ratio >= THRESH_SIDE:
            return CharacterType.SIDE
        elif ratio >= THRESH_RECURRING:
            return CharacterType.RECURRING
        else:
            return CharacterType.GUEST


class CharacterTool(Tool):
    """Tool for analyzing characters in the database."""

    def get_character_types(self) -> dict[Character, CharacterType]:
        """Get the type of each character based on their number of episode appearances."""
        total_episodes = self.session.query(func.count(Episode.id)).scalar()
        if total_episodes is None or total_episodes == 0:
            return {}

        results = (
            self.session.query(
                Character,
                func.count(func.distinct(Line.episode_id)).label("episode_count"),
            )
            .outerjoin(Line, Character.id == Line.character_id)
            .group_by(Character.id)
            .all()
        )

        types = {
            character: CharacterType.classify(n, total_episodes)
            for character, n in results
        }

        return types

    def get_characters(
        self,
        type: Optional[CharacterType] = None,
    ) -> list[Character]:
        """Get all characters, optionally filtered by type."""
        character_types = self.get_character_types()
        if type is None:
            return list(character_types.keys())

        return [
            character
            for character, char_type in character_types.items()
            if char_type == type
        ]

    def sort_characters_by_lines(
        self,
        characters: list[Character],
    ) -> list[tuple[Character, int]]:
        """Sort characters by the number of lines they have."""
        results = (
            self.session.query(
                Character,
                func.count(Line.id).label("line_count"),
            )
            .outerjoin(Line, Character.id == Line.character_id)
            .filter(Character.id.in_([c.id for c in characters]))
            .group_by(Character.id)
            .order_by(func.count(Line.id).desc())
            .all()
        )

        return results
