from abc import ABC
from abc import abstractmethod
from aoptk.pdf import PDF

class GetPDF(ABC):
    @abstractmethod
    def pdfs(self) -> list[PDF]:
        pass
