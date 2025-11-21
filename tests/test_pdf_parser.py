import pytest
from aoptk.get_publication import GetPublication
from aoptk.pdf_parser import ParsePDF


def test_parsepdf_is_subclass_of_getpublication():
    """Test inheritance structure."""
    assert issubclass(ParsePDF, GetPublication)


def test_cannot_instantiate_abstract_parsepdf():
    """Test can't instantiate ABC."""
    with pytest.raises(TypeError):
        ParsePDF()
