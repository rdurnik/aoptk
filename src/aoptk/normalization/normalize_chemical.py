from abc import ABC
from abc import abstractmethod
from aoptk.chemical import Chemical


class NormalizeChemical(ABC):
    """Abstract base class for chemical name normalization."""

    @abstractmethod
    def normalize_chemical(self, chemical: Chemical) -> Chemical:
        """Normalize a chemical name."""
        ...
