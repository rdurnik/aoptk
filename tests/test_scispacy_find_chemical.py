from __future__ import annotations
import os
import pytest
from aoptk.find_chemical import FindChemical
from aoptk.scispacy_find_chemical import ScispacyFindChemical


def test_can_create():
    """Can create ScispacyFindChemical instance."""
    actual = ScispacyFindChemical()
    assert actual is not None


def test_implements_interface():
    """ScispacyFindChemical implements FindChemical interface."""
    assert isinstance(ScispacyFindChemical(), FindChemical)


def test_find_chemical_not_empty():
    """Test that find_chemical method returns a non-empty result."""
    actual = ScispacyFindChemical().find_chemical("")
    assert actual is not None


IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


@pytest.mark.skipif(
    IN_GITHUB_ACTIONS, reason="Skip in Github Actions to save energy consumption (large model download required)."
)
@pytest.mark.parametrize(
    ("sentence", "expected"),
    [
        ("Thioacetamide was studied for its effect on liver cells.", ["thioacetamide"]),
        ("HepaRG cells were used as an experimental model.", []),
        (
            "Thioacetamide, carbon tetrachloride and ethanol were used to induce liver injury.",
            ["thioacetamide", "carbon tetrachloride", "ethanol"],
        ),
    ],
)
def test_find_chemical_one_chemical(sentence: str, expected: list[str]):
    """Test that find_chemical method finds chemicals in text."""
    assert os.getenv("GITHUB_URL") is None
    actual = [chem.name for chem in ScispacyFindChemical().find_chemical(sentence)]
    assert actual == expected
