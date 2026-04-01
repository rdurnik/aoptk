from __future__ import annotations
from abc import ABC
from abc import abstractmethod


class ConvertImage(ABC):
    """Abstract base class for converting image to text."""

    @abstractmethod
    def convert_image(self) -> str:
        """Return converted text data."""
        ...
