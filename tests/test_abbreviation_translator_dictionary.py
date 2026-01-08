from __future__ import annotations
import pytest
from aoptk.abbreviations.abbreviation_translator import AbbreviationTranslator
from aoptk.abbreviations.abbreviation_translator_dictionary import AbbreviationTranslatorDictionary


def test_can_create():
    """Test creation of AbbreviationTranslatorDictionary instance."""
    actual = AbbreviationTranslatorDictionary({})
    assert actual is not None


def test_implements_interface():
    """Test that AbbreviationTranslatorDictionary implements AbbreviationTranslator interface."""
    assert issubclass(AbbreviationTranslatorDictionary, AbbreviationTranslator)


def test_get_abstract_not_empty():
    """Test that translate_abbreviation method returns a non-empty result."""
    actual = AbbreviationTranslatorDictionary({}).translate_abbreviation("")
    assert actual is not None


@pytest.fixture
def test_dict():
    """Provide a test dictionary of abbreviations and their full forms."""
    return {
        "CCL4": "carbon tetrachloride",
        "FFA": "free fatty acids",
        "HSC": "hepatic stellate cell",
        "TAA": "thioacetamide",
        "MT": "microtissue",
        "MTX": "methotrexate",
        "ECM": "extracellular matrix",
        "Nrf2": "nuclear factor E2-related factor 2",
        "CD44": "cluster of Differentiation 44",
    }


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("One of the chemicals studied was TAA.", "One of the chemicals studied was thioacetamide."),
        ("TAA is a chemical compound.", "thioacetamide is a chemical compound."),
        (
            "TAA was studied in this study. TAA was found to be toxic to HepG2 cells.",
            "thioacetamide was studied in this study. thioacetamide was found to be toxic to HepG2 cells.",
        ),
        (
            "Combination of TAA, CCL4 and FFA was used on HSCs.",
            "Combination of thioacetamide, carbon tetrachloride and "
            "free fatty acids was used on hepatic stellate cells.",
        ),
        (
            "Extracellular matrix remodelling expected during the progression of fibrosis was "
            "observed in the MTs treated with the model compounds. Gene expression of MTs treated "
            "with MTX and TAA showed significant, dose-dependent transcriptional induction of"
            " collagen I, collagen IV, fibronectin I and CD44 (Fig 8).",
            "Extracellular matrix remodelling expected during the progression of fibrosis was "
            "observed in the microtissues treated with the model compounds. Gene expression of microtissues treated "
            "with methotrexate and thioacetamide showed significant, dose-dependent transcriptional induction of"
            " collagen I, collagen IV, fibronectin I and cluster of Differentiation 44 (Fig 8).",
        ),
        (
            "In addition to the effects on viability and ECM, the involvement of oxidative stress and the activation"
            " of the Nrf2 pathway in liver fibrosis have previously been reported [10]. The induction of Nrf2 and"
            " Keap-1 after exposure to MTX and TAA clearly indicates that this cellular defence mechanism is active"
            " in our culture system.",
            "In addition to the effects on viability and extracellular matrix, the involvement of oxidative stress "
            "and the activation"
            " of the nuclear factor E2-related factor 2 pathway in liver fibrosis have previously been reported [10]. "
            "The induction of nuclear factor E2-related factor 2 and"
            " Keap-1 after exposure to methotrexate and thioacetamide clearly indicates that this cellular "
            "defence mechanism is active"
            " in our culture system.",
        ),
    ],
)
def test_translates_known_abbreviations(test_dict: dict[str, str], text: str, expected: str):
    """Test that known abbreviations are correctly translated to their full forms."""
    actual = AbbreviationTranslatorDictionary(test_dict).translate_abbreviation(text)
    assert actual == expected
