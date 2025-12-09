import pytest
from aoptk.regex_sentence_generator import RegexSentenceGenerator
from aoptk.sentence_generator import SentenceGenerator


def test_can_create():
    """Test that RegexSentenceGenerator can be instantiated."""
    actual = RegexSentenceGenerator()
    assert actual is not None


def test_implements_interface():
    """Test that RegexSentenceGenerator implements SentenceGenerator interface."""
    assert issubclass(RegexSentenceGenerator, SentenceGenerator)


def test_generate_sentences_not_empty():
    """Test that generate_sentences method returns a non-empty result."""
    actual = RegexSentenceGenerator().tokenize("")
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
    actual = [sentence.__str__() for sentence in RegexSentenceGenerator().tokenize(text)]
    assert actual == expected
