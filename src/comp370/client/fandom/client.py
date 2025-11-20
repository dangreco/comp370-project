from dataclasses import dataclass

from .session import Session
from .services import CharacterService


@dataclass
class Client:
    session: Session = Session()

    def characters(self) -> CharacterService:
        return CharacterService(self.session)
