from abc import ABC
from abc import abstractmethod

class ProvideNormalizationDataframe(ABC):
    @abstractmethod
    def provide_normalization_dataframe(self):
        pass

