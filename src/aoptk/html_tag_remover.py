from bs4 import BeautifulSoup
from aoptk.cleaning import CleanText


class HTMLTagRemover(CleanText):
    """Class to remove HTML tags from text."""

    def __init__(self) -> str:
        pass

    def clean_text(self, text: str) -> str:
        """Remove HTML tags from the input text."""
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text()
