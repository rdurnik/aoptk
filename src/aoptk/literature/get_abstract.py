from __future__ import annotations
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from aoptk.literature.id import ID
from aoptk.literature.pdf import PDF

if TYPE_CHECKING:
    from aoptk.literature.abstract import Abstract


class GetAbstract(ABC):
    """Abstract base class for retrieving abstract data."""

    @abstractmethod
    def get_abstracts(self, ids: list[ID] | list[PDF]) -> list[Abstract]:
        """Return abstract data."""
        ...
