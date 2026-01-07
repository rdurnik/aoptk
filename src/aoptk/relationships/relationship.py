from dataclasses import dataclass
from aoptk.chemical import Chemical
from aoptk.effect import Effect


@dataclass
class Relationship:
    """Data structure representing a relationship between a chemical and an effect."""

    relationship: str
    chemical: Chemical
    effect: Effect

    def __str__(self) -> str:
        return self.relationship
