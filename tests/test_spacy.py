from __future__ import annotations
import os
import pytest
from aoptk.find_chemical import FindChemical
from aoptk.sentence_generator import SentenceGenerator
from aoptk.spacy import Spacy

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


pytestmark = pytest.mark.skipif(
    IN_GITHUB_ACTIONS,
    reason="Skip in Github Actions to save energy consumption (large model download required).",
)


def test_can_create():
    """Can create ScispacyFindChemical instance."""
    actual = Spacy()
    assert actual is not None


def test_implements_interface_find_chemical():
    """ScispacyFindChemical implements FindChemical interface."""
    assert isinstance(Spacy(), FindChemical)


def test_find_chemical_not_empty():
    """Test that find_chemical method returns a non-empty result."""
    actual = Spacy().find_chemical("")
    assert actual is not None


@pytest.mark.parametrize(
    ("sentence", "expected"),
    [
        ("Thioacetamide was studied for its effect on liver cells.", ["thioacetamide"]),
        ("HepaRG cells were used as an experimental model.", []),
        (
            "Thioacetamide, carbon tetrachloride and ethanol were used to induce liver injury.",
            ["thioacetamide", "carbon tetrachloride", "ethanol"],
        ),
        ("Thioacetamide causes cancer.", ["thioacetamide"]),
    ],
)
def test_find_chemical_one_chemical(sentence: str, expected: list[str]):
    """Test that find_chemical method finds chemicals in text."""
    actual = [chem.name for chem in Spacy().find_chemical(sentence)]
    assert actual == expected


def test_implements_interface_sentence_generator():
    """Test that Spacy implements SentenceGenerator interface."""
    assert issubclass(Spacy, SentenceGenerator)


def test_generate_sentences_not_empty():
    """Test that generate_sentences method returns a non-empty result."""
    actual = Spacy().generate_sentences("")
    assert actual is not None


@pytest.fixture(
    params=[
        (
            "This is the first sentence. This is the second sentence.",
            ["This is the first sentence.", "This is the second sentence."],
        ),
        (
            "The rational design and selective self-assembly"
            " of flexible and unsymmetric ligands into large "
            "coordination complexes is an eminent challenge"
            " in supramolecular coordination chemistry."
            " Here, we present the coordination-driven"
            " self-assembly of natural"
            " ursodeoxycholic-bile-acid-derived unsymmetric"
            " tris-pyridyl ligand (L) resulting in the selective "
            "and switchable formation of chiral stellated Pd6L8 "
            "and Pd12L16 cages. The selectivity of the cage "
            "originates in the adaptivity and flexibility of "
            "the arms of the ligand bearing pyridyl moieties. "
            "The interspecific transformations can be controlled"
            " by changes in the reaction conditions. The orientational"
            " self-sorting of L into a single constitutional isomer "
            "of each cage, i.e., homochiral quadruple and octuple "
            "right-handed helical species, was confirmed by a "
            "combination of molecular modelling and circular "
            "dichroism. The cages, derived from natural amphiphilic "
            "transport molecules, mediate the higher cellular uptake "
            "and increase the anticancer activity of bioactive "
            "palladium cations as determined in studies using in "
            "vitro 3D spheroids of the human hepatic cells HepG2.",
            [
                "The rational design and selective self-assembly of flexible "
                "and unsymmetric ligands into large coordination complexes is an "
                "eminent challenge in supramolecular coordination chemistry.",
                "Here, we present the coordination-driven self-assembly of "
                "natural ursodeoxycholic-bile-acid-derived unsymmetric tris-pyridyl"
                " ligand (L) resulting in the selective and switchable formation of "
                "chiral stellated Pd6L8 and Pd12L16 cages.",
                "The selectivity of the cage originates in the adaptivity and "
                "flexibility of the arms of the ligand bearing pyridyl moieties.",
                "The interspecific transformations can be controlled by changes in the reaction conditions.",
                "The orientational self-sorting of L into a single constitutional"
                " isomer of each cage, i.e., homochiral quadruple and octuple"
                " right-handed helical species, was confirmed by a combination"
                " of molecular modelling and circular dichroism.",
                "The cages, derived from natural amphiphilic transport molecules,"
                " mediate the higher cellular uptake and increase the anticancer "
                "activity of bioactive palladium cations as determined in studies "
                "using in vitro 3D spheroids of the human hepatic cells HepG2.",
            ],
        ),
        (
            "This is the first sentence. the author did not put capital T at the start.",
            ["This is the first sentence.", "the author did not put capital T at the start."],
        ),
        (
            "This is the first sentence.There is missing space after the period!",
            ["This is the first sentence.", "There is missing space after the period!"],
        ),
    ],
)
def sentence_cases(request: pytest.FixtureRequest):
    """Fixture providing test cases for sentence generation."""
    return request.param


def test_generate_sentences(sentence_cases: pytest.FixtureRequest):
    """Test generate_sentences method with various cases."""
    text, expected = sentence_cases
    actual = [sentence.sentence_text for sentence in Spacy().generate_sentences(text)]
    assert actual == expected
