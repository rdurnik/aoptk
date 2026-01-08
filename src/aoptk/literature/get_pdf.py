from __future__ import annotations
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aoptk.literature.pdf import PDF


class GetPDF(ABC):
    """Abstract base class for retrieving PDF data."""

    @abstractmethod
    def pdfs(self) -> list[PDF]:
        """Return a list of PDF paths."""
