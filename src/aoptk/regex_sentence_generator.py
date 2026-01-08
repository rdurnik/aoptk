from __future__ import annotations
import re
from aoptk.sentence import Sentence
from aoptk.sentence_generator import SentenceGenerator


class RegexSentenceGenerator(SentenceGenerator):
    """Generate sentences using regular expressions."""

    def tokenize(self, text: str) -> list[Sentence]:
        """Use regex to generate sentences."""
        sentences = re.split(r"(?<=[.!?])\s+|(?<=[.!?])(?=[A-Z])|<h4>|</h4>", str(text))
        return [Sentence(sentence.strip()) for sentence in sentences if sentence.strip()]
