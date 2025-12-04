from __future__ import annotations
import pytest
from aoptk.abbreviation_translator_dictionary_generator import AbbreviationDictionaryGenerator


def test_can_create():
    """Test creation of AbbreviationDictionaryGenerator instance."""
    actual = AbbreviationDictionaryGenerator("")
    assert actual is not None


def test_not_empty():
    """Test that provide_translation_dictionary method returns a non-empty result."""
    actual = AbbreviationDictionaryGenerator("").provide_translation_dictionary()
    assert actual is not None

def test_provide_list_of_abbreviations():
    """Test that provide_list_of_abbreviations method returns correct list of abbreviations."""
    text = "One of the chemicals studied was thioacetamide (TAA). TAA was found to be toxic to HepG2 cells."
    expected = ["TAA"]
    actual = [match.group(1) for match in AbbreviationDictionaryGenerator(text).provide_list_of_abbreviations()]
    assert actual == expected


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
        ("Transforming growth factor beta 1 (TGF-β1) was used to induce stellate cell activation",
          {"TGF-β1": "transforming growth factor beta 1"}),
        ("In addition, liver fibrosis is also a relevant toxicological outcome and has been "
        "identified as an Adverse Outcome Pathway (AOP), a novel tool in human risk assessment "
        "designed to provide mechanistic representation of critical toxicological effects [2,3].",
        {"AOP": "adverse outcome pathway"},
        ),
    ],
)
def test_provide_dictionary(text_abbreviations: str, expected: dict[str, str]):
    """Test that provide_translation_dictionary method generates correct abbreviation dictionary."""
    actual = AbbreviationDictionaryGenerator(text_abbreviations).provide_translation_dictionary()
    assert actual == expected
