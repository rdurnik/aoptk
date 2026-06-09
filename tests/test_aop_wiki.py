from __future__ import annotations
from aoptk.literature.databases.aop_wiki import AOPWiki
from aoptk.literature.get_abstract import GetAbstract
from aoptk.literature.id import ID


def test_can_create():
    """Test that AOPWiki can be instantiated."""
    actual = AOPWiki()
    assert actual is not None


def test_implements_interface():
    """Test that AOPWiki implements GetAbstract interface."""
    assert issubclass(AOPWiki, GetAbstract)


def test_get_abstracts():
    """Test that AOP 38 has the correct title."""
    abstracts = AOPWiki().get_abstracts()
    aop_38 = next(abstract for abstract in abstracts if abstract.id == ID("https://identifiers.org/aop/38"))
    min_length_of_abstract = 2000
    min_number_of_abstracts = 500
    assert aop_38.text.startswith("Protein Alkylation leading to Liver Fibrosis")
    assert len(aop_38.text) > min_length_of_abstract
    assert len(abstracts) > min_number_of_abstracts
