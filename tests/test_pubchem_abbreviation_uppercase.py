import pytest
from aoptk.chemical import Chemical
from aoptk.normalization.pubchem_abbreviation_uppercase import PubChemAbbreviationUppercase
from aoptk.normalization.pubchem_api import PubChemAPI


def test_can_create():
    """Test that PubChemAbbreviationsUppercase can be instantiated."""
    actual = PubChemAbbreviationUppercase()
    assert actual is not None


def test_implements_interface():
    """Test that PubChemAbbreviationsUppercase implements PubChemAPI."""
    assert issubclass(PubChemAbbreviationUppercase, PubChemAPI)


def test_normalize_chemical_not_empty():
    """Test that normalize_chemical method returns a non-empty result."""
    actual = PubChemAbbreviationUppercase().normalize_chemical(Chemical(""))
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
    """Test _is_uppercase method."""
    actual = PubChemAbbreviationUppercase().is_uppercase(chemical)
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
    assert PubChemAbbreviationUppercase().normalize_chemical(Chemical(suspected_abbreviation)) == expected
