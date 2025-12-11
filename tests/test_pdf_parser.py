import pytest
from aoptk.literature.get_publication import GetPublication
from aoptk.literature.pdf_parser import PDFParser


def test_parsepdf_is_subclass_of_getpublication():
    """Test inheritance structure."""
    assert issubclass(PDFParser, GetPublication)


def test_cannot_instantiate_abstract_parsepdf():
    """Test can't instantiate ABC."""
    with pytest.raises(TypeError):
        PDFParser()
