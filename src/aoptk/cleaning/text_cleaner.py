from __future__ import annotations
from abc import abstractmethod


class TextCleaner:
    """Abstract base class for cleaning text."""

    @abstractmethod
    def clean(self, text: str) -> str:
        """Return a cleaned version of the input text."""


class CleaningPipeline(TextCleaner):
    """Cleaning pipeline, combining various text clears into a single function."""

    def __init__(self, cleaners: list[TextCleaner]):
        self.cleaners = cleaners

    def clean(self, text: str) -> str:
        """Clean text using all cleaners in the pipeline.

        Args:
            text (str): Text to clean.

        Returns:
            str: Cleaned text after applying all cleaners.
        """
        cleaned = text
        for cleaner in self.cleaners:
            cleaned = cleaner.clean(cleaned)
        return cleaned
