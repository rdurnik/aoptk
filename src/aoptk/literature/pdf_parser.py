from aoptk.literature.get_abstract import GetAbstract
from aoptk.literature.get_publication import GetPublication


class PDFParser(GetPublication, GetAbstract):
    """Abstract base class for parsing PDF files."""
