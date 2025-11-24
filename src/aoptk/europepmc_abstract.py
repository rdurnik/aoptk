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
        all_abstracts: list[Abstract] = []
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
            json_data = response.json()
            results = json_data.get("resultList", {}).get("result", [])
            for record in results:
                abstract = record.get("abstractText", "")
                all_abstracts.append(Abstract(abstract))
            next_cursor = json_data.get("nextCursorMark")
            if not results or not next_cursor or next_cursor == cursor_mark:
                break
            cursor_mark = next_cursor
        return all_abstracts
