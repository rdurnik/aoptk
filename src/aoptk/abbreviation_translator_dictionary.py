from __future__ import annotations
import re
from aoptk.abbreviation_translator import AbbreviationTranslator


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
                matches = list(re.finditer(pattern, translated_text, flags=re.IGNORECASE))
                translated_text = self.fix_capitalization(translated_text, replacement, matches)
        return translated_text

    def fix_capitalization(
        self,
        translated_text: str,
        replacement: str,
        matches: list,
        sentence_end_offset: int = 2,
    ) -> str:
        """Fix capitalization of the translated abbreviations based on their position in the text."""
        for match in reversed(matches):
            start_pos = match.start()
            end_pos = match.end()

            if start_pos == 0 or (
                start_pos >= sentence_end_offset
                and translated_text[start_pos - sentence_end_offset : start_pos - 1] in ".!?"
            ):
                new_text = replacement.capitalize()
            else:
                new_text = replacement.lower()

            translated_text = translated_text[:start_pos] + new_text + translated_text[end_pos:]
        return translated_text
