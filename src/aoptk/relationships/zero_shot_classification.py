from __future__ import annotations
from itertools import product
from typing import TYPE_CHECKING
from transformers import pipeline
from aoptk.relationships.find_relationship import FindRelationships
from aoptk.relationships.relationship import Relationship

if TYPE_CHECKING:
    from aoptk.chemical import Chemical
    from aoptk.effect import Effect


class ZeroShotClassification(FindRelationships):
    """Zero-shot classification for finding relationships between chemicals and effects in text."""

    task = "zero-shot-classification"

    def __init__(self, 
                 text: str, 
                 chemicals: list[Chemical], 
                 effects: list[Effect], 
                 model: str = "facebook/bart-large-mnli",
                 threshold: float = 0.6,
                 margin: float = 0.15):
        self.text = text
        self.chemicals = chemicals
        self.effects = effects
        self.model = model
        self.classifier = pipeline(self.task, model)
        self.threshold = threshold
        self.margin = margin

    def find_relationships(self) -> list[Relationship]:
        """Find relationships between chemicals and effects using zero-shot classification."""
        relationships = []
        for chemical, effect in product(self.chemicals, self.effects):
            relationship = self._classify_relationship(chemical, effect)
            if relationship:
                relationships.append(relationship)
        return relationships

    def _classify_relationship(self, chemical: Chemical, effect: Effect) -> Relationship | None:
        """Classify the relationship between a chemical and effect.
        
        Returns:
            Relationship object if confidence thresholds are met, None otherwise.
        """
        candidate_labels = [
            f"{chemical} induces {effect}",
            f"{chemical} does not induce {effect}",
            f"{chemical} prevents or does not prevent {effect}",
        ]

        result = self.classifier(self.text, candidate_labels)
        top_label = result["labels"][0]
        top_score = result["scores"][0]
        second_score = result["scores"][1]

        if top_score < self.threshold or (top_score - second_score) < self.margin:
            return None

        if top_label == candidate_labels[0]:
            relationship_type = "positive"
        elif top_label == candidate_labels[1]:
            relationship_type = "negative"
        else:
            return None

        return Relationship(
            relationship=relationship_type,
            chemical=chemical,
            effect=effect,
        )
