from aoptk.sentence import Sentence


class Slide:
    """Slide data structure."""

    def __init__(self, sentences: list[Sentence]):
        self._text = " ".join([sentence.text for sentence in sentences])

    @property
    def text(self) -> str:
        """Return the slide's text."""
        return self._text
