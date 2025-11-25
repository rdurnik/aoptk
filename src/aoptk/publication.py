from dataclasses import dataclass
from aoptk.abstract import Abstract
from aoptk.id import ID


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
