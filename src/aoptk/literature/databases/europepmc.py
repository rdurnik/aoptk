from __future__ import annotations
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import ClassVar
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from aoptk.literature.abstract import Abstract
from aoptk.literature.get_abstract import GetAbstract
from aoptk.literature.get_id import GetID
from aoptk.literature.get_pdf import GetPDF
from aoptk.literature.id import ID
from aoptk.literature.pdf import PDF
from aoptk.literature.publication_metadata import PublicationMetadata
from aoptk.literature.utils import get_pubmed_pdf_url


class EuropePMC(GetAbstract, GetPDF, GetID):
    """Class to get PDFs from EuropePMC based on a query."""

    page_size = 1000
    timeout = 10
    headers: ClassVar = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
    }

    def __init__(self, query: str, storage: str = "tests/pdf_storage"):
        self._query = query
        self.storage = storage
        Path(self.storage).mkdir(parents=True, exist_ok=True)

        self._session = requests.Session()
        self._session.headers.update(self.headers)
        retry_strategy = Retry(
            total=5,
            backoff_factor=10,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("https://", adapter)

        self.id_list = self.get_id()

    def pdfs(self) -> list[PDF]:
        """Retrieve PDFs based on the query."""
        return [pdf for pdf in (self.get_pdf(publication_id) for publication_id in self.id_list) if pdf is not None]

    def get_abstracts(self) -> list[Abstract]:
        """Retrieve Abstracts based on the query."""
        return [
            abstract
            for abstract in (self.get_abstract(publication_id) for publication_id in self.id_list)
            if abstract is not None
        ]

    def get_publications_metadata(self) -> list[PublicationMetadata]:
        """Retrieve Publication metadata based on the query."""
        return [
            publication_metadata
            for publication_metadata in (
                self.get_publication_metadata(publication_id) for publication_id in self.id_list
            )
            if publication_metadata is not None
        ]

    def get_id(self) -> list[ID]:
        """Get a list of publication IDs from EuropePMC based on the query."""
        cursor_mark = "*"
        id_list = []

        while True:
            data_europepmc = self.call_api(cursor_mark, "idlist", self._query)
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
        response = self._session.get(
            f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={publication_id}&blobtype=pdf",
            stream=True,
            timeout=self.timeout,
        )
        if not response.ok and publication_id.isdecimal():
            pubmed_url = get_pubmed_pdf_url(publication_id)
            if pubmed_url:
                response = self._session.get(pubmed_url, stream=True, timeout=self.timeout)
                if not response.ok:
                    return None

        return self.write(publication_id, response)

    def write(self, publication_id: str, response: requests.Response) -> PDF:
        """Write the PDF content to a file and return a PDF object."""
        filepath = Path(self.storage) / f"{publication_id}.pdf"
        with filepath.open("wb") as f:
            f.writelines(response.iter_content(chunk_size=8192))
        return PDF(filepath)

    def get_abstract(self, publication_id: str) -> Abstract:
        """Return abstract from Europe PMC for a given publication ID."""
        cursor_mark = "*"

        json_data = self.call_api(cursor_mark, "core", publication_id)
        results = json_data.get("resultList", {}).get("result", [])

        if results:
            return Abstract(results[0].get("abstractText", ""), publication_id=ID(publication_id))
        return Abstract("", publication_id=ID(publication_id))

    def call_api(self, cursor_mark: str, result_type: str, query: str) -> dict:
        """Call the EuropePMC web api to query the search.

        Args:
            cursor_mark (str): Parameter for pagination.
            result_type (str): Whether to search for idlists or core.
            query (str): main query to carry out - default self._query

        Returns:
            dict: JSON response
        """
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        params = {
            "query": query,
            "format": "json",
            "pageSize": self.page_size,
            "cursorMark": cursor_mark,
            "resultType": result_type,
        }
        response = self._session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_publication_metadata(self, publication_id: str) -> PublicationMetadata:
        """Return abstract from Europe PMC for a given publication ID."""
        cursor_mark = "*"

        json_data = self.call_api(cursor_mark, "core", publication_id)
        results = json_data.get("resultList", {}).get("result", [])

        if results:
            publication_id = results[0].get("id")
            publication_date = results[0].get("pubYear") or "Unknown"
            title = results[0].get("title")
            authors = results[0].get("authorString", "")
            database = "Europe PMC"
            search_date = datetime.now(timezone.utc)
            return PublicationMetadata(
                publication_id=publication_id,
                publication_date=publication_date,
                title=title,
                authors=authors,
                database=database,
                search_date=search_date,
            )
        return None


def _get_publication_id(result: dict) -> str | None:
    return result.get("pmcid") or result.get("pmid") or result.get("id")
