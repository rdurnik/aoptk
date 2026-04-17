from __future__ import annotations
from abc import ABC
from abc import abstractmethod


class ConvertImage(ABC):
    """Abstract base class for converting image to text."""

    @abstractmethod
    def convert_image(self, image_path: str) -> str:
        """Return converted text data.

        Args:
            image_path: Path to the image file to be converted.
        """
        ...
