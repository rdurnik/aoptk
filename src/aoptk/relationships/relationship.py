from dataclasses import dataclass
from aoptk.chemical import Chemical
from aoptk.effect import Effect
from aoptk.relationship_type import RelationshipType


@dataclass
class Relationship:
    """Data structure representing relationship between a chemical and an effect."""

    relationship_type: RelationshipType
    chemical: Chemical
    effect: Effect
    context: str


    def __str__(self) -> str:
        return f"Evidence(relationship_type={self.relationship_type}, chemical={self.chemical.name}, effect={self.effect.name}, context={self.context})"
    