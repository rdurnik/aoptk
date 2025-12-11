import pytest
from aoptk.chemical import Chemical
from aoptk.normalize_chemical import NormalizeChemical
from aoptk.pubchem_abbreviations import PubChemAbbreviations


def test_can_create():
    """Test that PubChemAbbreviations can be instantiated."""
    actual = PubChemAbbreviations()
    assert actual is not None


def test_implements_interface():
    """Test that PubChemAbbreviations implements NormalizeChemical interface."""
    assert issubclass(PubChemAbbreviations, NormalizeChemical)


def test_normalize_chemical_not_empty():
    """Test that normalize_chemical method returns a non-empty result."""
    actual = PubChemAbbreviations().normalize_chemical(Chemical(""))
    assert actual is not None


@pytest.mark.parametrize(
    ("chemical", "expected"),
    [
        ("acetaminophen", False),
        ("TAA", True),
        ("CCL4", True),
        ("Thioacetamide", False),
    ],
)
def test_check_uppercase(chemical: str, expected: str):
    """Test is_uppercase method."""
    actual = PubChemAbbreviations().is_uppercase(chemical)
    assert actual == expected


@pytest.mark.parametrize(
    ("suspected_abbreviation", "expected"),
    [
        ("TAA", "thioacetamide"),
        ("CCL4", "carbon tetrachloride"),
        ("MTX", "methotrexate"),
        ("thioacetamide", "thioacetamide"),
        ("Thioacetamide", "Thioacetamide"),
        ("somethingnotinpubchem", "somethingnotinpubchem"),
    ],
)
def test_normalize_chemical(suspected_abbreviation: str, expected: str):
    """Test normalize_chemical method with various entities."""
    assert PubChemAbbreviations().normalize_chemical(Chemical(suspected_abbreviation)) == expected
