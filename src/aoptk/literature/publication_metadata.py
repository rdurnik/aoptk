from dataclasses import dataclass
from aoptk.literature.id import ID
from datetime import datetime


@dataclass
class Publication_metadata:
    """Data structure representing a publication."""

    publication_id: ID
    publication_date: int
    title: str
    authors: list[str]
    database: str
    search_date: datetime

    def __str__(self) -> str:
        return self.title