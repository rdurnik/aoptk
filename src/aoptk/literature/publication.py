from dataclasses import dataclass
from aoptk.literature.abstract import Abstract
from aoptk.literature.id import ID


@dataclass
class Publication:
    """Data structure representing a publication."""

    id: ID
    abstract: Abstract
    full_text: str
    abbreviations: dict
    tables: list
    figures: list
    figure_descriptions: list

    def __str__(self) -> str:
        return self.abstract
