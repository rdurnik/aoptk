from abc import ABC
from abc import abstractmethod
from aoptk.publication import Publication


class GetPublication(ABC):
    """Abstract base class for retrieving publication data."""
    @abstractmethod
    def get_publication(self) -> Publication:
        """Return publication data."""
