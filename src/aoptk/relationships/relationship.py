from dataclasses import dataclass
from aoptk.chemical import Chemical
from aoptk.effect import Effect


@dataclass
class Relationship:
    """Data structure representing relationship between a chemical and an effect."""

    relationship_type: str
    chemical: Chemical
    effect: Effect
    context: str

    def __str__(self) -> str:
        return (
            f"relationship_type={self.relationship_type}, "
            f"chemical={self.chemical.name}, effect={self.effect.name}, "
            f"context={self.context})"
        )
