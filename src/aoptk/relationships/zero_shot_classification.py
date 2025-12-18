from __future__ import annotations
from typing import TYPE_CHECKING
from transformers import pipeline
from aoptk.relationships.find_relationship import FindRelationships
from aoptk.relationships.relationship import Relationship

if TYPE_CHECKING:
    from aoptk.chemical import Chemical
    from aoptk.effect import Effect


class ZeroShotClassification(FindRelationships):
    """Zero-shot classification for finding relationships between chemicals and effects in text."""

    threshold = 0.6
    margin = 0.15
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    def __init__(self, text: str, chemicals: list[Chemical], effects: list[Effect]):
        self.text = text
        self.chemicals = chemicals
        self.effects = effects

    def find_relationships(self) -> list[Relationship]:
        """Find relationships between chemicals and effects using zero-shot classification."""
        relationships = []
        for effect in self.effects:
            for chemical in self.chemicals:
                candidate_labels = [
                    f"{chemical} induces {effect}",
                    f"{chemical} does not induce {effect}",
                    f"{chemical} prevents or does not prevent {effect}",
                ]

                result = self.classifier(self.text, candidate_labels)

                labels = result["labels"]
                scores = result["scores"]

                top_label = labels[0]
                top_score = scores[0]
                second_score = scores[1]

                if top_score >= self.threshold and (top_score - second_score) >= self.margin:
                    if top_label == candidate_labels[0]:
                        relationship_type = "positive"
                    elif top_label == candidate_labels[1]:
                        relationship_type = "negative"
                    else:
                        continue

                    relationships.append(
                        Relationship(
                            relationship=relationship_type,
                            chemical=chemical,
                            effect=effect,
                        ),
                    )
        return relationships
