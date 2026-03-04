class Sentence:
    """Sentece data structure."""

    def __init__(self, text: str):
        self.text = text

    def __str__(self) -> str:
        """Return the sentence's text."""
        return self.text
