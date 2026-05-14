from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from aoptk.literature.id import ID


@dataclass
class PublicationMetadata:
    """Data structure representing a publication."""

    id: ID
    publication_date: str
    title: str
    authors: str
    database: str
    search_date: datetime

    def __str__(self) -> str:
        return self.title
