from aoptk.abbreviation_translator import AbbreviationTranslator
from aoptk.abbreviation_translator_dictionary import AbbreviationTranslatorDictionary
import pytest

def test_can_create():
    actual = AbbreviationTranslatorDictionary({}, '')
    assert actual is not None

def test_implements_interface():
    assert issubclass(AbbreviationTranslatorDictionary, AbbreviationTranslator)

def test_get_abstract_not_empty():
    actual = AbbreviationTranslatorDictionary({}, '').translate_abbreviation()
    assert actual is not None

@pytest.fixture
def test_dict():
    return {
        "CCL4": "carbon tetrachloride",
        "FFA": "free fatty acids",
        "HSC": "hepatic stellate cell",
        "TAA": "thioacetamide"
    }

@pytest.mark.parametrize(
    ("text", "expected"),
    [
    ("One of the chemicals studied was TAA.", "One of the chemicals studied was thioacetamide."),
    ("TAA is a chemical compound.", "Thioacetamide is a chemical compound."),
    ("TAA was studied in this study. TAA was found to be toxic to HepG2 cells.", "Thioacetamide was studied in this study. Thioacetamide was found to be toxic to HepG2 cells."),
    ("Combination of TAA, CCL4 and FFA was used on HSCs.", "Combination of thioacetamide, carbon tetrachloride and free fatty acids was used on hepatic stellate cells."),
    ]
)

def test_translates_known_abbreviations(test_dict, text, expected):
    actual = AbbreviationTranslatorDictionary(test_dict, text).translate_abbreviation()
    assert actual == expected