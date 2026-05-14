from __future__ import annotations
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from aoptk.literature.id import ID

if TYPE_CHECKING:
    from aoptk.literature.pdf import PDF


class GetPDF(ABC):
    """Abstract base class for retrieving PDF data."""

    @abstractmethod
    def get_pdfs(self, ids: list[ID]) -> list[PDF]:
        """Return a list of PDF paths."""
