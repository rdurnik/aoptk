from __future__ import annotations
import requests
from aoptk.abstract import Abstract
from aoptk.get_abstract import GetAbstract


class EuropePMCAbstract(GetAbstract):
    """Retrieve abstracts from Europe PMC based on a query."""

    def __init__(self, query: str):
        self._query = query

    def get_abstracts(self) -> list[Abstract]:
        """Return abstracts from Europe PMC based on the query."""
        page_size = 1000
        cursor_mark = "*"
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        while True:
            params = {
                "query": self._query,
                "format": "json",
                "pageSize": page_size,
                "cursorMark": cursor_mark,
                "resultType": "core",
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            json = response.json()
            results = json.get("resultList", {}).get("result", [])
            abstracts = []
            for record in results:
                abstract = record.get("abstractText", "")
                abstracts.append(Abstract(abstract))
            return abstracts
