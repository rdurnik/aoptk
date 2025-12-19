from __future__ import annotations
from itertools import product
from typing import TYPE_CHECKING
from transformers import pipeline
from aoptk.chemical import Chemical
from aoptk.effect import Effect
from aoptk.relationships.find_relationship import FindRelationships
from aoptk.relationships.relationship import Relationship

if TYPE_CHECKING:
    from aoptk.chemical import Chemical
    from aoptk.effect import Effect


class ZeroShotClassification(FindRelationships):
    """Zero-shot classification for finding relationships between chemicals and effects in text."""

    task = "zero-shot-classification"
    default_relationships = (
        "induces",
        "does not induce",
        "prevents or does not prevent",
        "has no known association with",
    )

    def __init__(
        self,
        relationships: list[str] | None = None,
        model: str = "facebook/bart-large-mnli",
        threshold: float = 0.6,
        margin: float = 0.15,
    ):
        self.relationships = relationships if relationships is not None else self.default_relationships
        self.model = model
        self.threshold = threshold
        self.margin = margin
        self.classifier = pipeline(self.task, model)

    def find_relationships(self, text: str, chemicals: list[Chemical], effects: list[Effect]) -> list[Relationship]:
        """Find relationships between chemicals and effects using zero-shot classification."""
        relationships = []
        for chemical, effect in product(chemicals, effects):
            if relationship := self._classify_relationship(text, chemical, effect):
                relationships.append(relationship)
        return relationships

    def _classify_relationship(self, text: str, chemical: Chemical, effect: Effect) -> Relationship | None:
        """Classify the relationship between a chemical and an effect."""
        candidate_labels = [f"{chemical} {relationship} {effect}" for relationship in self.relationships]

        result = self.classifier(text, candidate_labels)

        labels = result["labels"]
        scores = result["scores"]

        top_label = labels[0]
        top_score = scores[0]
        second_score = scores[1]

        if self._is_prediction_confident_enough(top_score, second_score) and (
            relationship_type := self._select_relationship_type(top_label, candidate_labels)
        ):
            return Relationship(relationship=relationship_type, chemical=chemical, effect=effect)
        return None

    def _is_prediction_confident_enough(self, top_score: int, second_score: int) -> bool:
        """Check if the prediction is confident enough based on threshold and margin."""
        return top_score >= self.threshold and (top_score - second_score) >= self.margin

    def _select_relationship_type(self, top_label: str, candidate_labels: list[str]) -> str | None:
        """Select the relationship type based on the top label."""
        if top_label == candidate_labels[0]:
            return "positive"
        if top_label == candidate_labels[1]:
            return "negative"
        return None
