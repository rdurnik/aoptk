from __future__ import annotations
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aoptk.literature.publication import Publication


class GetPublication(ABC):
    """Abstract base class for retrieving publication data."""

    @abstractmethod
    def get_publications(self) -> list[Publication]:
        """Return publication data."""
        ...
