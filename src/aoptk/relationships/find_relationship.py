from __future__ import annotations
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
import pandas as pd

if TYPE_CHECKING:
    from aoptk.chemical import Chemical
    from aoptk.effect import Effect
    from aoptk.relationships.relationship import Relationship


class FindRelationships(ABC):
    """Interface for finding relationships in text."""

    @abstractmethod
    def find_relationships(self, text: str, chemicals: list[Chemical], effects: list[Effect]) -> list[Relationship]:
        """Find relationships between chemicals and effects in the given text."""

    @abstractmethod
    def find_relationships_in_image(
        self,
        image_path: str,
        chemicals: list[Chemical],
        effects: list[Effect],
    ) -> list[Relationship]:
        """Find relationships between chemicals and effects in the text extracted from the given image."""

    @abstractmethod
    def find_relationships_in_table(
        self,
        table_data: pd.DataFrame,
        effects: list[Effect],
    ) -> list[Relationship]:
        """Find relationships between chemicals and effects in the given table data."""
