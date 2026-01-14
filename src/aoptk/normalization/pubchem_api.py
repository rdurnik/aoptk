from __future__ import annotations
from typing import TYPE_CHECKING
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from aoptk.normalization.normalize_chemical import NormalizeChemical

if TYPE_CHECKING:
    from aoptk.chemical import Chemical


class PubChemAPI(NormalizeChemical):
    """Use PubChem API to normalize chemical names."""

    timeout = 10

    def __init__(self):
        self._session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("https://", adapter)

    def normalize_chemical(self, chemical: Chemical) -> Chemical:
        """Use the PubChem API to normalize a chemical name.

        This method may modify the given ``chemical`` instance in-place by
        updating its ``heading`` attribute when a title is found in PubChem.
        The same ``chemical`` instance that is passed in is returned.
        """
        if title_name := self._find_title_in_pubchem(chemical.name):
            chemical.heading = title_name
        return chemical

    def _find_title_in_pubchem(self, chemical_name: str) -> str | None:
        """Find the title chemical name from PubChem."""
        search_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{chemical_name}/property/Title/TXT"
        response = self._session.get(search_url, timeout=self.timeout)
        if not response.ok:
            return chemical_name
        return response.text.strip().lower()
