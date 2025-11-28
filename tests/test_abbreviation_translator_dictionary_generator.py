from __future__ import annotations
import pytest
from aoptk.abbreviation_translator_dictionary_generator import AbbreviationDictionaryGenerator


def test_can_create():
    """Test creation of AbbreviationDictionaryGenerator instance."""
    actual = AbbreviationDictionaryGenerator("")
    assert actual is not None


def test_get_abstract_not_empty():
    """Test that provide_translation_dictionary method returns a non-empty result."""
    actual = AbbreviationDictionaryGenerator("").provide_translation_dictionary()
    assert actual is not None


@pytest.mark.parametrize(
    ("text_abbreviations", "expected"),
    [
        (
            "One of the chemicals studied was thioacetamide (TAA). TAA was found to be toxic to HepG2 cells.",
            {"TAA": "thioacetamide"},
        ),
        ("Carbon tetrachloride (CCL4) is a chemical compound.", {"CCL4": "carbon tetrachloride"}),
        (
            "Carbon tetrachloride (CCL4), thioacetamide (TAA) are chemical compounds.",
            {"CCL4": "carbon tetrachloride", "TAA": "thioacetamide"},
        ),
    ],
)
def test_provide_dictionary(text_abbreviations: str, expected: dict[str, str]):
    """Test that provide_translation_dictionary method generates correct abbreviation dictionary."""
    actual = AbbreviationDictionaryGenerator(text_abbreviations).provide_translation_dictionary()
    assert actual == expected
