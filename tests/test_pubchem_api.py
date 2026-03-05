import pytest
from aoptk.chemical import Chemical
from aoptk.normalization.normalize_chemical import NormalizeChemical
from aoptk.normalization.pubchem_api import PubChemAPI


def test_can_create():
    """Test that PubChemAbbreviations can be instantiated."""
    actual = PubChemAPI()
    assert actual is not None


def test_implements_interface():
    """Test that PubChemAbbreviations implements NormalizeChemical interface."""
    assert issubclass(PubChemAPI, NormalizeChemical)


def test_normalize_chemical_not_empty():
    """Test that normalize_chemical method returns a non-empty result."""
    actual = PubChemAPI().normalize_chemical(Chemical(""))
    assert actual is not None


@pytest.mark.parametrize(
    ("chemical_name", "expected_heading", "synonyms"),
    [
        ("TAA", "thioacetamide", {"acetimidic acid, thio-"}),
        ("CCL4", "carbon tetrachloride", {"tetrachlormethan"}),
        ("MTX", "methotrexate", {"methotrexatum"}),
        ("thioacetamide", "thioacetamide", {"acetimidic acid, thio-"}),
        ("Thioacetamide", "thioacetamide", {"acetimidic acid, thio-"}),
        ("somethingnotinpubchem", "somethingnotinpubchem", {""}),
        ("paracetamol", "acetaminophen", {"acetaminophen"}),
    ],
)
def test_normalize_chemical(chemical_name: str, expected_heading: str, synonyms: set[str]):
    """Test normalize_chemical method with various entities."""
    actual = PubChemAPI().normalize_chemical(Chemical(chemical_name))
    assert actual.heading == expected_heading
    assert synonyms.issubset(actual.synonyms)
