from __future__ import annotations
from abc import ABC
from abc import abstractmethod
from typing import Self
from aoptk.text_generation_api import TextGenerationAPI


class TextGenerationInjector(ABC):
    """Abstract base class for injecting text generation into PDF scan conversion."""

    @abstractmethod
    def inject_text_generation(self, text_generation: TextGenerationAPI) -> Self:
        """Inject the text generation dependency.

        Args:
            text_generation (TextGenerationAPI): The text generation API.

        Returns:
            Self: The instance with the text generation dependency injected.
        """
        ...
