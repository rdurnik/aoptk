from abc import ABC
from abc import abstractmethod

class GetPublicationData(ABC):
    @abstractmethod
    def get_publication_data(self):
        pass
