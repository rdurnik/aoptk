from __future__ import annotations
from abc import ABC
from abc import abstractmethod


class CategorizeText(ABC):
    """Abstract base class for categorizing text."""

    @abstractmethod
    def categorize_text(self, text: str, categories: list[str]) -> str | None:
        """Categorize the given text into one of the specified categories.

        Args:
            text (str): The text to categorize.
            categories (list[str]): The list of available categories.

        Returns:
            str | None: The categorized label or None if no match is found.
        """
        ...
