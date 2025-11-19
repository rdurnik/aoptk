from abc import ABC
from abc import abstractmethod
from aoptk.get_publication import GetPublication

class ParsePDF(ABC, GetPublication):
    @abstractmethod
    def get_publication(self):
        pass

    @abstractmethod
    def _parse_pdf(self, pdf):
        pass
