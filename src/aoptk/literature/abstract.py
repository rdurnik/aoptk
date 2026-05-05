from __future__ import annotations
from dataclasses import dataclass
from aoptk.literature.id import ID


@dataclass
class Abstract:
    """Data structure representing an abstract."""

    id: ID
    text: str

    def __str__(self) -> str:
        return self.text
