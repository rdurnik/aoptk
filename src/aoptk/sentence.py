class Sentence:
    """Sentece data structure."""

    def __init__(self, text: str):
        self._text = text

    @property
    def text(self) -> str:
        """Return the sentence's text."""
        return self._text
