from __future__ import annotations
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aoptk.sentence import Sentence


class SentenceGenerator(ABC):
    """Sentence generator base class."""

    @abstractmethod
    def tokenize(self, text: str) -> list[Sentence]:
        """Return sentence data."""
        ...
