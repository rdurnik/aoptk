import pytest
from aoptk.chemical import Chemical
from aoptk.normalization.pubchem_abbreviation_short import PubChemAbbreviationShort
from aoptk.normalization.pubchem_api import PubChemAPI


def test_can_create():
    """Test that PubChemAbbreviationShort can be instantiated."""
    actual = PubChemAbbreviationShort()
    assert actual is not None


def test_implements_interface():
    """Test that PubChemAbbreviationShort implements PubChemAPI."""
    assert issubclass(PubChemAbbreviationShort, PubChemAPI)


def test_normalize_chemical_not_empty():
    """Test that normalize_chemical method returns a non-empty result."""
    actual = PubChemAbbreviationShort().normalize_chemical(Chemical(""))
    assert actual is not None


@pytest.mark.parametrize(
    ("chemical", "expected"),
    [
        ("acetaminophen", False),
        ("TAA", True),
        ("CCL4", True),
        ("PCB-126", True),
        ("B(a)P", True),
        ("B[a]P", True),
        ("Thioacetamide", False),
    ],
)
def test_check_short_length(chemical: str, expected: str):
    """Test _is_short method."""
    actual = PubChemAbbreviationShort().is_short(chemical)
    assert actual == expected


@pytest.mark.parametrize(
    ("suspected_abbreviation", "expected"),
    [
        ("TAA", "thioacetamide"),
        ("CCL4", "carbon tetrachloride"),
        ("MTX", "methotrexate"),
        ("B(a)P", "benzo[a]pyrene"),
        ("PFOA", "perfluorooctanoic acid"),
        ("2,3,7,8-TCDD", "2,3,7,8-tetrachlorodibenzo-p-dioxin"),
        ("thioacetamide", "thioacetamide"),
        ("Thioacetamide", "Thioacetamide"),
        ("somethingnotinpubchem", "somethingnotinpubchem"),
    ],
)
def test_normalize_chemical(suspected_abbreviation: str, expected: str):
    """Test normalize_chemical method with various entities."""
    assert PubChemAbbreviationShort().normalize_chemical(Chemical(suspected_abbreviation)) == expected
