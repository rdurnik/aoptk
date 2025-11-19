from dataclasses import dataclass
from aoptk.abstract import Abstract
from aoptk.id import ID

@dataclass
class Publication:
    id: ID
    abstract: Abstract
    full_text: str
    abbreviations: dict
    tables: list
    figures: list
    figure_description: dict

    def __str__(self) -> str:
        pass
