from abc import ABC
from abc import abstractmethod
from aoptk.get_publication import GetPublication
from aoptk.publication import Publication

class ParsePDF(ABC, GetPublication):
    @abstractmethod
    def get_publication(self) -> Publication:
        pass

    @abstractmethod
    def _parse_pdf(self, pdf) -> str:
        pass
