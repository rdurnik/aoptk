from __future__ import annotations
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from aoptk.literature.id import ID
from aoptk.literature.pdf import PDF

if TYPE_CHECKING:
    from aoptk.literature.publication import Publication


class GetPublication(ABC):
    """Abstract base class for retrieving publication data."""

    @abstractmethod
    def get_publications(self, ids: list[ID] | list[PDF]) -> list[Publication]:
        """Return publication data."""
        ...
