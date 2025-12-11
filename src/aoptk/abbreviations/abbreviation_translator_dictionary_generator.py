from __future__ import annotations
import re


class AbbreviationDictionaryGenerator:
    """Generates a dictionary of abbreviations and their full forms from text.

    text: Input text that should be translated.
    window: Number of words to the left of the abbreviation to consider for translating.
    """

    def __init__(self, text: str, window: int = 5):
        self.text = text
        self.window = window
        self.translation_dictionary = self.provide_translation_dictionary()

    def provide_translation_dictionary(self) -> dict[str, str]:
        """Generate a dictionary mapping abbreviations to their full forms."""
        abbreviations_dict = {}
        for text_in_brackets in self.provide_list_of_abbreviations():
            abbreviation = text_in_brackets.group(1).strip()
            left_words = self.find_words_left_of_abbreviation(text_in_brackets)
            first_letter_of_the_abbreviation = abbreviation[0].lower()
            if full_form := self.extract_full_form(
                left_words,
                first_letter_of_the_abbreviation,
            ):
                abbreviations_dict[abbreviation] = full_form.lower()
        return abbreviations_dict

    def provide_list_of_abbreviations(self) -> list[str]:
        """Find words in brackets that start with a capital letter or a number."""
        return re.finditer(r"\(([A-ZΑ-Ω0-9][A-Za-z0-9\-α-ωΑ-Ω]*)\)", self.text)

    def extract_full_form(self, left_words: list[str], first_letter_of_the_abbreviation: str) -> str | None:
        """Extract all words to the right of the rightmost letter matching the first letter of the abbreviation."""
        start_idx = self.find_rightmost_letter_matching_first_letter_of_abbreviation(
            left_words,
            first_letter_of_the_abbreviation,
        )
        if start_idx is not None:
            candidate_words = left_words[start_idx:]
            return " ".join(candidate_words) if candidate_words else None
        return None

    def find_rightmost_letter_matching_first_letter_of_abbreviation(
        self,
        left_words: list[str],
        first_letter_of_the_abbreviation: str,
    ) -> int | None:
        """Find the index of the rightmost word whose first letter matches the first letter of the abbreviation."""
        for i in reversed(range(len(left_words))):
            if left_words[i][0].lower() == first_letter_of_the_abbreviation:
                return i
        return None

    def find_words_left_of_abbreviation(self, text_in_brackets: re.Match) -> list[str]:
        """Find words to the left of the abbreviation within a specified window."""
        words = re.findall(r"[A-Za-z0-9\-α-ωΑ-Ω]+", self.text[: text_in_brackets.start()])
        return words[-self.window :]
