from __future__ import annotations
import re
from aoptk.abbreviations.abbreviation_translator import AbbreviationTranslator


class AbbreviationTranslatorDictionary(AbbreviationTranslator):
    """Translates abbreviations in text using a provided dictionary."""

    def __init__(self, pdf_dictionary: dict[str, str]):
        self.pdf_dictionary = pdf_dictionary

    def translate_abbreviation(self, text: str) -> str:
        """Translate abbreviations in the text using the provided dictionary."""
        translated_text = text

        for abbreviation, full_form in self.pdf_dictionary.items():
            patterns = [
                (r"\b" + re.escape(abbreviation) + r"s\b", full_form + "s"),
                (r"\b" + re.escape(abbreviation) + r"\b", full_form),
            ]
            for pattern, replacement in patterns:
                translated_text = re.sub(pattern, replacement, translated_text, flags=re.IGNORECASE)

        return translated_text
