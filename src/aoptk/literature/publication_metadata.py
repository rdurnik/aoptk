from __future__ import annotations
from dataclasses import dataclass

if __name__ == "__main__":
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from datetime import datetime
        from aoptk.literature.id import ID


@dataclass
class PublicationMetadata:
    """Data structure representing a publication."""

    publication_id: ID
    publication_date: int
    title: str
    authors: list[str]
    database: str
    search_date: datetime

    def __str__(self) -> str:
        return self.title
