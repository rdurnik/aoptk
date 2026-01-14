from __future__ import annotations
from typing import TYPE_CHECKING
from aoptk.normalization.pubchem_api import PubChemAPI

if TYPE_CHECKING:
    from aoptk.chemical import Chemical


class PubChemAbbreviationUppercase(PubChemAPI):
    """Find chemical abbreviations via PubChem. Check for uppercase as a condition of an abbreviation."""

    def __init__(self):
        super().__init__()

    def normalize_chemical(self, chemical: Chemical) -> Chemical:
        """Return a full-form of a chemical name if the original name is in uppercase."""
        if self.is_uppercase(chemical.name):
            return super().normalize_chemical(chemical)
        return chemical

    def is_uppercase(self, chemical: str) -> bool:
        """Check if the chemical name is uppercase."""
        return chemical.isupper()
