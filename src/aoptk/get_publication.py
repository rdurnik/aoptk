from abc import ABC
from abc import abstractmethod

from aoptk.publication import Publication


class GetPublications(ABC):
    @abstractmethod
    def publications(self) -> list[Publication]:
        pass
