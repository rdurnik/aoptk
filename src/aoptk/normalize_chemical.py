from abc import ABC
from abc import abstractmethod

class NormalizeChemical(ABC):
    @abstractmethod
    def normalize_chemical(self):
        pass


    