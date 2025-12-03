from abc import abstractmethod


class CleanText:
    """Abstract base class for cleaning text."""

    @abstractmethod
    def clean(self, text: str) -> str:
        """Return a cleaned version of the input text."""


class CleaningPipeline(CleanText):

    def __init__(self, cleaners: list[CleanText]):
        self.cleaners = cleaners
    
    def clean(self, text: str) -> str:
        cleaned = text
        for cleaner in self.cleaners:
            cleaned = cleaner.clean(cleaned)
        return cleaned