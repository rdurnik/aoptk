from abc import abstractmethod


class TextCleaner:
    """Abstract base class for cleaning text."""

    @abstractmethod
    def clean(self, text: str) -> str:
        """Return a cleaned version of the input text."""
