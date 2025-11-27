from aoptk.abbreviation_translator import AbbreviationTranslator
import re

class AbbreviationTranslatorDictionary(AbbreviationTranslator):
    def __init__(self, pdf_dictionary: dict[str, str], text: str):
        self.pdf_dictionary = pdf_dictionary
        self.text = text

    def translate_abbreviation(self) -> str:
        translated_text = self.text
        
        for abbreviation, full_form in self.pdf_dictionary.items():
            patterns = [
                (r'\b' + re.escape(abbreviation) + r's\b', full_form + 's'),  
                (r'\b' + re.escape(abbreviation) + r'\b', full_form)          
            ]    
            for pattern, replacement in patterns:
                matches = list(re.finditer(pattern, translated_text, flags=re.IGNORECASE))
                translated_text = self.fix_capitalization(translated_text, replacement, matches)
        return translated_text

    def fix_capitalization(self, translated_text: str, replacement: str, matches: list) -> str:
        for match in reversed(matches):
            start_pos = match.start()
            end_pos = match.end()
                    
            if start_pos == 0:
                new_text = replacement.capitalize()
            elif start_pos >= 2 and translated_text[start_pos - 2:start_pos - 1] in '.!?':
                new_text = replacement.capitalize()
            else:
                new_text = replacement.lower()
                    
            translated_text = translated_text[:start_pos] + new_text + translated_text[end_pos:]
        return translated_text

    