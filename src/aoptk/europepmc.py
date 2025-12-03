from __future__ import annotations
from pathlib import Path
import requests
from aoptk.abstract import Abstract
from aoptk.get_abstract import GetAbstract
from aoptk.get_pdf import GetPDF
from aoptk.pdf import PDF
from aoptk.utils import get_pubmed_pdf_url


class EuropePMC(GetPDF, GetAbstract):
    """Class to get PDFs from EuropePMC based on a query."""

    page_size = 1000
    timeout = 10

    def __init__(self, query: str, storage: str = "tests/pdf_storage"):
        self._query = query
        self.storage = storage
        Path(self.storage).mkdir(parents=True, exist_ok=True)

        self.id_list = self.get_id_list()

    def pdfs(self) -> list[PDF]:
        """Retrieve PDFs based on the query."""
        return [pdf for pdf in (self.get_pdf(publication_id) for publication_id in self.id_list) if pdf is not None]

    def get_id_list(self) -> list[str]:
        """Get a list of publication IDs from EuropePMC based on the query."""
        cursor_mark = "*"
        id_list = []

        while True:
            data_europepmc = self.call_api(cursor_mark, "idlist")
            results = data_europepmc.get("resultList", {}).get("result", [])

            id_list.extend([_get_publication_id(result) for result in results])

            next_cursor = data_europepmc.get("nextCursorMark")
            if not next_cursor or next_cursor == cursor_mark:
                break
            cursor_mark = next_cursor

        return id_list

    def remove_reviews(self) -> EuropePMC:
        """Modify the query to exclude review articles."""
        self._query += ' NOT PUB_TYPE:"Review"'
        return self

    def abstracts_only(self) -> EuropePMC:
        """Modify the query to search in the text of abstracts only."""
        self._query = "ABSTRACT:(" + self._query + ")"
        return self

    def get_pdf(self, publication_id: str) -> PDF | None:
        """Retrieve the PDF for a given publication ID."""
        response = requests.get(
            f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={publication_id}&blobtype=pdf",
            stream=True,
            timeout=self.timeout,
        )
        if not response.ok and publication_id.isdecimal():
            pubmed_url = get_pubmed_pdf_url(publication_id)
            if pubmed_url:
                response = requests.get(pubmed_url, stream=True, timeout=self.timeout)
                if not response.ok:
                    return None

        return self.write(publication_id, response)

    def write(self, publication_id: str, response: requests.Response) -> PDF:
        """Write the PDF content to a file and return a PDF object."""
        filepath = Path(self.storage) / f"{publication_id}.pdf"
        with filepath.open("wb") as f:
            f.writelines(response.iter_content(chunk_size=8192))
        return PDF(filepath)

    def get_abstracts(self) -> list[Abstract]:
        """Return abstracts from Europe PMC based on the query."""
        cursor_mark = "*"
        all_abstracts: list[Abstract] = []

        while True:
            json_data = self.call_api(cursor_mark, "core")
            results = json_data.get("resultList", {}).get("result", [])

            all_abstracts.extend([Abstract(record.get("abstractText", "")) for record in results])
            next_cursor = json_data.get("nextCursorMark")
            if not results or not next_cursor or next_cursor == cursor_mark:
                break
            cursor_mark = next_cursor
        return all_abstracts

    def call_api(self, cursor_mark: str, result_type: str) -> dict:
        """Call the EuropePMC web api to query the search.

        Args:
            cursor_mark (str): Parameter for pagination.
            result_type (str): Whether to search for idlists or core.

        Returns:
            dict: JSON response
        """
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        params = {
            "query": self._query,
            "format": "json",
            "pageSize": self.page_size,
            "cursorMark": cursor_mark,
            "resultType": result_type,
        }
        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()


def _get_publication_id(result: dict) -> str | None:
    return result.get("pmcid") or result.get("pmid") or result.get("id")
