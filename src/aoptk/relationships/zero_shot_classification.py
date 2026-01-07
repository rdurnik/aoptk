from abc import ABC, abstractmethod
from itertools import product

from transformers import pipeline

from aoptk.chemical import Chemical
from aoptk.effect import Effect
from aoptk.relationships.find_relationship import FindRelationships
from aoptk.relationships.relationship import Relationship


class ZeroShotClassification(FindRelationships, ABC):
    task = "zero-shot-classification"
    def __init__(
        self,
        relationships: list[str] | None,
        model: str,
        threshold: float,
    ):
        self.relationships = relationships
        self.model = model
        self.threshold = threshold
        self.classifier = pipeline(self.task, model)
    
    @abstractmethod
    def _classify_relationship(self, text: str, chemical: Chemical, effect: Effect) -> Relationship | None:
        ...

    def find_relationships(self, text: str, chemicals: list[Chemical], effects: list[Effect]) -> list[Relationship]:
        """Find relationships between chemicals and effects using zero-shot classification."""
        relationships = []
        for chemical, effect in product(chemicals, effects):
            if relationship := self._classify_relationship(text, chemical, effect):
                relationships.append(relationship)
        return relationships