from dataclasses import dataclass
from ..session import Session


@dataclass
class Service:
    session: Session
