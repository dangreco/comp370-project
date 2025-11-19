from dataclasses import dataclass

from .session import Session
from .services import SeasonService
from .services import EpisodeService


@dataclass
class Client:
    session: Session = Session()

    def seasons(self) -> SeasonService:
        return SeasonService(self.session)

    def episodes(self) -> EpisodeService:
        return EpisodeService(self.session)
