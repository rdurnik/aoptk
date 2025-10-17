from abc import ABC
from abc import abstractmethod

class NormalizeChemical(ABC):
    @abstractmethod
    def normalize_chemical(self):
        pass

    @abstractmethod
    def get_database_for_normalization(self):
        pass

    @abstractmethod
    def clean_database_for_normalization(self):
        pass

    