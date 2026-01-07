from __future__ import annotations
from aoptk.chemical import Chemical
from aoptk.normalization.pubchem_api import PubChemAPI


class PubChemAbbreviationUppercase(PubChemAPI):
    """Find chemical abbreviations via PubChem. Check for uppercase as a condition of an abbreviation."""

    def __init__(self):
        super().__init__()

    def normalize_chemical(self, chemical: Chemical) -> Chemical:
        """Return a full-form of a chemical name if the original name is in uppercase."""
        if self.is_uppercase(chemical.name):
            return super().normalize_chemical(chemical)
        return Chemical(chemical.name)

    def is_uppercase(self, chemical: str) -> bool:
        """Check if the chemical name is uppercase."""
        return chemical.isupper()
