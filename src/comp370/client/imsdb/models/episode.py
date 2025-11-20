from dataclasses import dataclass

import datetime


@dataclass
class Episode:
    number: int
    title: str
    date: datetime.date
    writers: list[str]
