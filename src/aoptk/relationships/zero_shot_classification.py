from __future__ import annotations
from abc import ABC
from abc import abstractmethod
from itertools import product
from typing import TYPE_CHECKING
import pandas as pd
from transformers import pipeline
from aoptk.relationships.find_relationship import FindRelationships

if TYPE_CHECKING:
    from aoptk.chemical import Chemical
    from aoptk.effect import Effect
    from aoptk.relationships.relationship import Relationship


class ZeroShotClassification(FindRelationships, ABC):
    """Base class for zero shot classification."""

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
    def _classify_relationship(self, text: str, chemical: Chemical, effect: Effect) -> Relationship | None: ...

    def find_relationships_in_text(
        self,
        text: str,
        chemicals: list[Chemical],
        effects: list[Effect],
    ) -> list[Relationship]:
        """Find relationships between chemicals and effects using zero-shot classification."""
        relationships = []
        for chemical, effect in product(chemicals, effects):
            if relationship := self._classify_relationship(text, chemical, effect):
                relationships.append(relationship)
        return relationships

    def find_relationships_in_image(
        self,
        image_path: str,
        chemicals: list[Chemical],
        effects: list[Effect],
    ) -> list[Relationship]:
        """Find relationships between chemicals and effects in an image."""
        msg = "Image relationship extraction is not implemented in ZeroShotClassification."
        raise NotImplementedError(msg)

    def find_relationships_in_table(
        self,
        table_data: pd.DataFrame,
        effects: list[Effect],
    ) -> list[Relationship]:
        """Find relationships between chemicals and effects in the given table data."""
        msg = "Table relationship extraction is not implemented in ZeroShotClassification."
        raise NotImplementedError(msg)

    def find_relationships_in_text_and_images(
        self,
        text: str,
        image_paths: list[str],
        effects: list[Effect],
    ) -> list[Relationship]:
        """Find relationships between chemicals and effects in the given text and images combined."""
        msg = "Text and image relationship extraction is not implemented in ZeroShotClassification."
        raise NotImplementedError(msg)
