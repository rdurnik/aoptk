from abc import ABC
from abc import abstractmethod
from aoptk.chemical import Chemical
from aoptk.relationship import Relationship
from aoptk.effect import Effect

class FindRelationships(ABC):
    """Interface for finding relationships in text."""

    @abstractmethod
    def find_relationships(self, text: str, chemicals: list[Chemical], effects: list[Effect]) -> list[Relationship]:
        """Find relationships between chemicals and effects in the given text."""