from abc import ABC
from abc import abstractmethod

class GetPDF(ABC):
    @abstractmethod
    def get_pdf(self):
        pass
