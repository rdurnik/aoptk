import pandas as pd
import pytest
from aoptk.chemical import Chemical
from aoptk.normalization.normalize_chemical import NormalizeChemical
from aoptk.normalization.pubchem_local import PubChemSynonyms


def test_can_create():
    """Test that PubChemSynonyms can be instantiated."""
    actual = PubChemSynonyms(None)
    assert actual is not None


def test_implements_interface():
    """Test that PubChemSynonyms implements NormalizeChemical interface."""
    assert issubclass(PubChemSynonyms, NormalizeChemical)


def test_normalize_chemical_not_empty():
    """Test that normalize_chemical method returns a non-empty result."""
    actual = PubChemSynonyms(pd.DataFrame()).normalize_chemical("")
    assert actual is not None


@pytest.fixture
def synonyms() -> pd.DataFrame:
    """Fixture providing a PubChem synonyms DataFrame."""
    content = {
        "heading": ["acetaminophen", "thioacetamide"],
        "synonyms": [["paracetamol", "acamol"], ["thiacetamid", "thioacetamid"]],
    }
    return pd.DataFrame(content)


@pytest.mark.parametrize(
    ("chemical", "expected"),
    [
        ("acetaminophen", "acetaminophen"),
        ("paracetamol", "acetaminophen"),
        ("thioacetamide", "thioacetamide"),
        (
            "something_not_in_the_database_but_recognized_as_chemical",
            "something_not_in_the_database_but_recognized_as_chemical",
        ),
    ],
)
def test_normalize_chemical_multiple_chemicals(chemical: str, expected: str, synonyms: pd.DataFrame):
    """Test normalize_chemical method with multiple chemicals."""
    sut = PubChemSynonyms(synonyms)
    actual = sut.normalize_chemical(Chemical(chemical))
    assert actual == expected
