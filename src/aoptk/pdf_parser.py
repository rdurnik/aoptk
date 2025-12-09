from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING
from aoptk.get_publication import GetPublication

if TYPE_CHECKING:
    from aoptk.publication import Publication


class ParsePDF(GetPublication):
    """Abstract base class for parsing PDF files."""

    @abstractmethod
    def get_publications(self) -> list[Publication]:
        """Return a Publication object parsed from the PDF."""
