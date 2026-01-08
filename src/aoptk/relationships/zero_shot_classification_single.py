from __future__ import annotations
from typing import TYPE_CHECKING
from aoptk.chemical import Chemical
from aoptk.effect import Effect
from aoptk.relationships.relationship import Relationship
from aoptk.relationships.zero_shot_classification import ZeroShotClassification

if TYPE_CHECKING:
    from aoptk.chemical import Chemical
    from aoptk.effect import Effect


class ZeroShotClassificationSingle(ZeroShotClassification):
    """Zero-shot classification for finding relationships between chemicals and effects in text.

    This version classifies a single relationship type at a time.
    """

    text_to_avoid_confusion_with_preventive_or_non_preventive = "prevents or does not prevent"

    def __init__(
        self,
        relationships: list[str] | None = ("induces", "does not induce"),
        model: str = "MoritzLaurer/deberta-v3-large-zeroshot-v2.0",
        threshold: float = 0.8,
    ):
        super().__init__(relationships, model, threshold)

    def _classify_relationship(self, text: str, chemical: Chemical, effect: Effect) -> Relationship | None:
        """Classify the relationship between a chemical and an effect."""
        hypothesis = f"{chemical} {{}} {effect}"
        hypothesis_verbs = list(self.relationships)

        for hypothesis_verb in hypothesis_verbs:
            verbs = self._add_verbs_to_avoid_confussion_with_preventive_or_non_preventive(hypothesis_verb)
            result = self.classifier(text, verbs, hypothesis_template=hypothesis, multi_label=False)

            top_label = result["labels"][0]
            top_score = result["scores"][0]

            if self._is_prediction_confident_enough(top_score) and (
                relationship_type := self._select_relationship_type(top_label, hypothesis_verbs)
            ):
                return Relationship(relationship=relationship_type, chemical=chemical, effect=effect)
        return None

    def _add_verbs_to_avoid_confussion_with_preventive_or_non_preventive(self, verb: str) -> list[str]:
        """Add verbs to avoid confusion with preventive or non-preventive relationships."""
        verbs = [verb]
        verbs.append(self.text_to_avoid_confusion_with_preventive_or_non_preventive)
        return verbs

    def _is_prediction_confident_enough(self, top_score: int) -> bool:
        """Check if the prediction is confident enough based on threshold and margin."""
        return top_score >= self.threshold

    def _select_relationship_type(self, top_label: str, classes_verbalized: list[str]) -> str | None:
        """Select the relationship type based on the top label."""
        if top_label == classes_verbalized[0]:
            return "positive"
        if top_label == classes_verbalized[1]:
            return "negative"
        return None
