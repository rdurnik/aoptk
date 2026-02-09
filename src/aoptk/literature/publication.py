from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
from aoptk.literature.abstract import Abstract
from aoptk.literature.id import ID


@dataclass
class Publication:
    """Data structure representing a publication."""

    id: ID
    abstract: Abstract
    full_text: str | list[str]
    abbreviations: dict
    tables: list[pd.DataFrame]
    figures: list
    figure_descriptions: list

    def __str__(self) -> str:
        return self.abstract
