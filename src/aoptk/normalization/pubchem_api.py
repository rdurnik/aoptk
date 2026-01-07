from __future__ import annotations
import requests
from aoptk.chemical import Chemical
from aoptk.normalization.normalize_chemical import NormalizeChemical


class PubChemAPI(NormalizeChemical):
    """Use PubChem API to normalize chemical names."""

    timeout = 10

    def __init__(self):
        self._session = requests.Session()

    def normalize_chemical(self, chemical: Chemical) -> Chemical:
        """Use PubChem API to normalize chemical names."""
        if title_name := self._find_title_in_pubchem(chemical.name):
            return Chemical(name=title_name)
        return Chemical(name=chemical.name)

    def _find_title_in_pubchem(self, chemical_name: str) -> str | None:
        """Find the title chemical name from PubChem."""
        search_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{chemical_name}/property/Title/TXT"
        response = self._session.get(search_url, timeout=self.timeout)
        if not response.ok:
            return chemical_name
        return response.text.strip().lower()
