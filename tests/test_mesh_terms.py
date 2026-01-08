import pandas as pd
import pytest
from aoptk.chemical import Chemical
from aoptk.normalization.mesh_terms import MeshTerms
from aoptk.normalization.normalize_chemical import NormalizeChemical


def test_can_create():
    """Test that MeshTerms can be instantiated."""
    actual = MeshTerms(None)
    assert actual is not None


def test_implements_interface():
    """Test that MeshTerms implements NormalizeChemical interface."""
    assert issubclass(MeshTerms, NormalizeChemical)


def test_normalize_chemical_not_empty():
    """Test that normalize_chemical method returns a non-empty result."""
    actual = MeshTerms(pd.DataFrame()).normalize_chemical("")
    assert actual is not None


@pytest.fixture
def mesh_terms():
    """Fixture providing a MeSH terms DataFrame."""
    content = {
        "heading": ["acetaminophen", "thioacetamide"],
        "mesh_terms": [["paracetamol", "acamol"], ["thiacetamid", "thioacetamid"]],
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
def test_normalize_chemical_multiple_chemicals(chemical: str, expected: str, mesh_terms: pd.DataFrame):
    """Test normalize_chemical method with multiple chemicals."""
    assert MeshTerms(mesh_terms).normalize_chemical(Chemical(chemical)) == expected
