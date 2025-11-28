from bs4 import BeautifulSoup
from aoptk.cleaning import CleanText


class HTMLTagRemover(CleanText):
    """Class to remove HTML tags from text."""

    def __init__(self, text: str) -> str:
        self.text = text

    def clean_text(self) -> str:
        """Remove HTML tags from the input text."""
        soup = BeautifulSoup(self.text, "html.parser")
        return soup.get_text()
