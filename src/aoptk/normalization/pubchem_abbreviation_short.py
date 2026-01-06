from __future__ import annotations
from aoptk.chemical import Chemical
from aoptk.normalization.pubchem_api import PubChemAPI


class PubChemAbbreviationShort(PubChemAPI):
    """Find chemical abbreviations via PubChem. Check for short length as a condition of an abbreviation."""

    def __init__(self):
        super().__init__()

    def normalize_chemical(self, chemical: Chemical) -> Chemical:
        """Return a Chemical with abbreviation set if name is uppercase."""
        if self._is_short(chemical.name):
            return super().normalize_chemical(chemical)
        return Chemical(chemical.name)

    def _is_short(self, chemical: str) -> bool:
        """Check if the chemical name is short."""
        cleaned = chemical.replace('-', '').replace('(', '').replace(')', '').replace('0', '').replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8', '').replace('9', '')
        return len(cleaned) < 5
