from __future__ import annotations
from abc import ABC
from abc import abstractmethod
from aoptk.sentence import Sentence
from aoptk.slide import Slide


class SlideGenerator(ABC):
    """Slide generator base class."""

    @abstractmethod
    def generate_slides(self, sentences: list[Sentence], number_of_sentences: int) -> list[Slide]:
        """Generate slides from a list of sentences."""
        ...
