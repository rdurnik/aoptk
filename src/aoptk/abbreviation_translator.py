from __future__ import annotations
from abc import ABC
from abc import abstractmethod


class AbbreviationTranslator(ABC):
    """Interface for translating abbreviations in text."""

    @abstractmethod
    def translate_abbreviation(self, text: str) -> str:
        """Translate abbreviations in given text."""
