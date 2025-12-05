class Sentence:
    """Sentece data structure."""

    def __init__(self, sentence_text: str):
        self._sentence_text = sentence_text

    @property
    def tokenize(self) -> str:
        """Return the sentence's text."""
        return self._sentence_text

    def __str__(self) -> str:
        """Return the sentence's text."""
        return self._sentence_text
