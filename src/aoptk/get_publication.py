from abc import ABC
from abc import abstractmethod
from aoptk.publication import Publication

class GetPublication(ABC):
    @abstractmethod
    def get_publication(self) -> Publication:
        pass