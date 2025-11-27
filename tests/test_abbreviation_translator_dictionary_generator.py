from aoptk.abbreviation_translator_dictionary_generator import AbbreviationDictionaryGenerator
import pytest

def test_can_create():
    actual = AbbreviationDictionaryGenerator('')
    assert actual is not None

def test_get_abstract_not_empty():
    actual = AbbreviationDictionaryGenerator('').provide_translation_dictionary()
    assert actual is not None

@pytest.mark.parametrize(
    ("text_abbreviations", "expected"),
    [
    ("One of the chemicals studied was thioacetamide (TAA). TAA was found to be toxic to HepG2 cells.", {'TAA': 'thioacetamide'}),
    ("Carbon tetrachloride (CCL4) is a chemical compound.", {'CCL4': 'carbon tetrachloride'}),
    ("Carbon tetrachloride (CCL4), thioacetamide (TAA) are chemical compounds.", {'CCL4': 'carbon tetrachloride', 'TAA': 'thioacetamide'}),
    ]
)

def test_provide_dictionary(text_abbreviations, expected):
    actual = AbbreviationDictionaryGenerator(text_abbreviations).provide_translation_dictionary()
    assert actual == expected
