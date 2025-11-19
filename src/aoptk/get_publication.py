from abc import ABC
from abc import abstractmethod


class GetPublication(ABC):
    @abstractmethod
    def get_publication(self):
        pass