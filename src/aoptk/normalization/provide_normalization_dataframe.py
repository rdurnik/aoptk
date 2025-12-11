from abc import ABC
from abc import abstractmethod
import pandas as pd


class ProvideNormalizationDataframe(ABC):
    """Abstract base class for providing normalization dataframe."""

    @abstractmethod
    def provide_normalization_dataframe(self) -> pd.DataFrame:
        """Provide a normalization dataframe."""
        ...
