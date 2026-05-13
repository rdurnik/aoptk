from __future__ import annotations
from dataclasses import dataclass
from typing import Literal


@dataclass
class Query:
    """Data structure representing a query."""

    search_term: str
    date: tuple[int, int, int] | None = None
    has_full_text: bool = False
    only_preprint: bool = False
    licensing: (
        Literal[
            "open-access",
            "CC0",
            "CC-BY",
            "CC-BY-SA",
            "CC-BY-ND",
            "CC-BY-NC",
            "CC-BY-NC-ND",
            "CC-BY-NC-SA",
        ]
        | None
    ) = None
    only_search_abstract_title: bool = False
