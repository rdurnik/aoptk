from aoptk.sentence import Sentence


class Slide:
    """Slide data structure."""

    def __init__(self, sentences: list[Sentence]):
        self.text = " ".join([sentence.text for sentence in sentences])

    def __str__(self) -> str:
        """Return the slide's text."""
        return self.text
