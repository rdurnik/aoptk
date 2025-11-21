from __future__ import annotations
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aoptk.chemical import Chemical


class FindChemical(ABC):
    """Interface for finding chemicals in text."""

    @abstractmethod
    def find_chemical(self, sentence: str) -> list[Chemical]:
        """Find chemicals in the given sentence."""
