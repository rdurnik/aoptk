import re

class AbbreviationDictionaryGenerator():
    def __init__(self, text: str, window: int = 5):
        self.text = text
        self.window = window
        self.translation_dictionary = self.provide_translation_dictionary()

    def provide_translation_dictionary(self) -> dict[str, str]:
        abbreviations_dict = {}
        for text_in_brackets in re.finditer(r'\(([A-Za-z0-9\-]+)\)', self.text):
            abbreviation = text_in_brackets.group(1).strip()
            left_words = self.find_words_left_of_abbreviation(text_in_brackets)
            first_letter_of_the_abbreviation = abbreviation[0].lower()
            
            if (start_idx := self.find_rightmost_letter_matching_first_letter_of_abbreviation(left_words, first_letter_of_the_abbreviation)) is not None:
                if expansion := self.extract_all_words_right_from_the_rightmost_letter(left_words, start_idx):
                    abbreviations_dict[abbreviation] = expansion.lower()

        return abbreviations_dict

    def extract_all_words_right_from_the_rightmost_letter(self, left_words, start_idx):
        expansion = None
        candidate_words = left_words[start_idx:]
        expansion = " ".join(candidate_words)
        return expansion

    def find_rightmost_letter_matching_first_letter_of_abbreviation(self, left_words, first_letter_of_the_abbreviation):
        start_idx = None
        for i in reversed(range(len(left_words))):
            if left_words[i][0].lower() == first_letter_of_the_abbreviation:
                start_idx = i
                break
        return start_idx

    def find_words_left_of_abbreviation(self, text_in_brackets):
        words = re.findall(r"[A-Za-z0-9\-]+", self.text[:text_in_brackets.start()])
        left_words = words[-self.window:]
        return left_words
