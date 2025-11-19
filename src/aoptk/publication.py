from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import Optional

from aoptk.abstract import Abstract


@dataclass
class Publication:
    id: str
    abstract: Abstract
    full_text: str
    abbreviations: Optional[Dict[str, str]] = field(default_factory=dict)
    tables: Optional[str] = None
    figures: Optional[str] = None
    figure_description: Optional[str] = None

    def __str__(self) -> str:
        pass # ?
