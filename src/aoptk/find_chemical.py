from abc import ABC
from abc import abstractmethod
from aoptk.chemical import Chemical


class FindChemical(ABC):
    @abstractmethod
    def find_chemical(self, sentence: str) -> list[Chemical]:
        pass