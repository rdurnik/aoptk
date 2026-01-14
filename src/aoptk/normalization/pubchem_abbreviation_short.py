from __future__ import annotations
from typing import TYPE_CHECKING
from aoptk.normalization.pubchem_api import PubChemAPI

if TYPE_CHECKING:
    from aoptk.chemical import Chemical


class PubChemAbbreviationShort(PubChemAPI):
    """Find chemical abbreviations via PubChem. Check for short length as a condition of an abbreviation."""

    characters_to_ignore = "-()0123456789[],"
    max_characters_allowed = 4

    def __init__(self):
        super().__init__()

    def normalize_chemical(self, chemical: Chemical) -> Chemical:
        """Return a full-form of a chemical name if the original name is short."""
        if self.is_short(chemical.name):
            return super().normalize_chemical(chemical)
        return chemical

    def is_short(self, chemical: str) -> bool:
        """Check if the chemical name is short."""
        translation_table = str.maketrans("", "", self.characters_to_ignore)
        cleaned = chemical.translate(translation_table)
        return len(cleaned) <= self.max_characters_allowed
