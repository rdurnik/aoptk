from __future__ import annotations
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from aoptk.literature.id import ID

if TYPE_CHECKING:
    from aoptk.literature.publication_metadata import PublicationMetadata


class GetPublicationMetadata(ABC):
    """Abstract base class for retrieving publication metadata."""

    @abstractmethod
    def get_publications_metadata(self, ids: list[ID]) -> list[PublicationMetadata]:
        """Return publication metadata."""
        ...
