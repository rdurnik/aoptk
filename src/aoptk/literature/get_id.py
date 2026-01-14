from __future__ import annotations
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aoptk.literature.id import ID


class GetID(ABC):
    """Abstract base class for retrieving IDs."""

    @abstractmethod
    def get_id(self) -> list[ID]:
        """Return a list of IDs."""
