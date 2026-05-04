from __future__ import annotations
import xml.etree.ElementTree as ET
import zipfile
from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import ClassVar
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from aoptk.literature.abstract import Abstract
from aoptk.literature.get_abstract import GetAbstract
from aoptk.literature.get_id import GetID
from aoptk.literature.get_pdf import GetPDF
from aoptk.literature.get_publication import GetPublication
from aoptk.literature.get_publication_metadata import GetPublicationMetadata
from aoptk.literature.id import ID
from aoptk.literature.pdf import PDF
from aoptk.literature.publication import Publication
from aoptk.literature.publication_metadata import PublicationMetadata
from aoptk.literature.utils import is_europepmc_id


class EuropePMC(GetAbstract, GetPDF, GetID, GetPublication, GetPublicationMetadata):
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
    image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")

    def __init__(
        self,
        query: str,
        storage: str,
        figure_storage: str,
    ):
        self._query = query
        self.storage = storage
        self.figure_storage = figure_storage
        Path(self.storage).mkdir(parents=True, exist_ok=True)
        Path(self.figure_storage).mkdir(parents=True, exist_ok=True)

        self._session = requests.Session()
        self._session.headers.update(self.headers)
        retry_strategy = Retry(
            total=10,
            backoff_factor=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("https://", adapter)

        self.id_list = self.get_ids()

    def get_pdfs(self) -> list[PDF]:
        """Retrieve PDFs based on the query."""
        return [pdf for pdf in (self._get_pdf(publication_id) for publication_id in self.id_list) if pdf is not None]

    def get_abstracts(self) -> list[Abstract]:
        """Retrieve Abstracts based on the query."""
        return [
            abstract
            for abstract in (self._get_abstract(publication_id) for publication_id in self.id_list)
            if abstract is not None
        ]

    def get_publications(self) -> list[Publication]:
        """Retrieve Publications based on the query."""
        return [
            publication
            for publication in (self._get_publication(publication_id) for publication_id in self.id_list)
            if publication is not None
        ]

    def get_publications_metadata(self) -> list[PublicationMetadata]:
        """Retrieve Publication metadata based on the query."""
        return [
            publication_metadata
            for publication_metadata in (
                self._get_publication_metadata(publication_id) for publication_id in self.id_list
            )
            if publication_metadata is not None
        ]

    def get_ids(self) -> list[ID]:
        """Get a list of publication IDs from EuropePMC based on the query."""
        cursor_mark = "*"
        id_list = []

        while True:
            data_europepmc = self._call_api(cursor_mark, "idlist", self._query)
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

    def _get_pdf(self, publication_id: str) -> PDF | None:
        """Retrieve the PDF for a given publication ID.

        Args:
            publication_id (str): The ID of the publication for which to retrieve the PDF.

        Returns:
            PDF | None: The PDF object if successful, None otherwise.
        """
        if is_europepmc_id(publication_id):
            response = self._session.get(
                f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={publication_id}&blobtype=pdf",
                stream=True,
                timeout=self.timeout,
            )
            if response.ok:
                return self._write_pdf(publication_id, response)
            return None
        return None

    def _write_pdf(self, publication_id: str, response: requests.Response) -> PDF:
        """Write the PDF content to a file and return a PDF object.

        Args:
            publication_id (str): The ID of the publication for which the PDF is being written.
            response (requests.Response): The HTTP response containing the PDF content.
        """
        filepath = Path(self.storage) / f"{publication_id}.pdf"
        with filepath.open("wb") as f:
            f.writelines(response.iter_content(chunk_size=8192))
        return PDF(filepath)

    def _get_abstract(self, publication_id: str) -> Abstract:
        """Return abstract from Europe PMC for a given publication ID.

        Args:
            publication_id (str): The ID of the publication for which to retrieve the abstract.

        Returns:
            Abstract: The abstract object if successful, None otherwise.
        """
        cursor_mark = "*"

        json_data = self._call_api(cursor_mark, "core", publication_id)
        results = json_data.get("resultList", {}).get("result", [])

        if results:
            return Abstract(results[0].get("abstractText", ""), publication_id=ID(publication_id))
        return Abstract("", publication_id=ID(publication_id))

    def _call_api(self, cursor_mark: str, result_type: str, query: str) -> dict:
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

    def _get_publication_metadata(self, publication_id: str) -> PublicationMetadata | None:
        """Return abstract from Europe PMC for a given publication ID.

        Args:
            publication_id (str): The ID of the publication to retrieve metadata for.
        """
        cursor_mark = "*"

        json_data = self._call_api(cursor_mark, "core", publication_id)
        results = json_data.get("resultList", {}).get("result", [])

        if results:
            publication_id = results[0].get("id")
            publication_date = results[0].get("pubYear") or "Unknown"
            title = results[0].get("title")
            authors = results[0].get("authorString", "")
            database = "Europe PMC"
            search_date = datetime.now(UTC)
            return PublicationMetadata(
                publication_id=publication_id,
                publication_date=publication_date,
                title=title,
                authors=authors,
                database=database,
                search_date=search_date,
            )
        return None

    def _get_publication(self, publication_id: str) -> Publication | None:
        """Return a Publication object for a given publication ID.

        Args:
            publication_id (str): The ID of the publication to retrieve.
        """
        if xml_tree := self._get_xml(publication_id):
            root = xml_tree.getroot()
            return Publication(
                id=publication_id,
                abstract=self._parse_xml_abstract(root),
                full_text=self._parse_xml_full_text(root),
                figures=self._get_figures(publication_id),
                figure_descriptions=self._parse_xml_figure_descriptions(root),
                tables=self._parse_xml_tables(root),
            )
        return None

    def _parse_xml_abstract(self, root: ET.Element) -> str:
        """Return the full text content of the first <abstract> element as a single string.

        Args:
            root (ET.Element): The root element of the XML tree.
        """
        if (abstract_elem := root.find(".//abstract")) is not None:
            return " ".join(abstract_elem.itertext()).strip()
        return ""

    def _parse_xml_full_text(self, root: ET.Element) -> str:
        """Parse the XML content to extract the full text.

        Args:
            root (ET.Element): The root element of the XML tree.
        """
        lines = []

        for element in root.iter():
            if element.tag in {"title", "p"}:
                text = "".join(element.itertext()).strip()
                if text:
                    lines.append(text)

        return "\n\n".join(lines)

    def _parse_xml_figure_descriptions(self, root: ET.Element) -> str:
        """Parse the XML content to extract the figure descriptions.

        Args:
            root (ET.Element): The root element of the XML tree.
        """
        lines = []

        for element in root.iter():
            if element.tag == "fig":
                text = "".join(element.itertext()).strip()
                if text:
                    lines.append(text)

        return "\n\n".join(lines)

    def _parse_xml_tables(self, root: ET.Element) -> list[pd.DataFrame]:
        """Parse the XML content to extract tables as a list of DataFrames, preserving order.

        Args:
            root (ET.Element): The root element of the XML tree.
        """
        tables = []
        for element in root.iter():
            if element.tag == "table-wrap" and (table_elem := element.find(".//table")) is not None:
                rows = self._extract_rows(table_elem)
                df = pd.DataFrame(rows)
                tables.append(df)
        return tables

    def _extract_rows(self, table_elem: ET.Element) -> list[list[str]]:
        """Extract rows from a table element, preserving order.

        Args:
            table_elem (ET.Element): The XML element representing the table.
        """
        rows = []
        for row in table_elem.findall(".//tr"):
            cells = ["".join(cell.itertext()).strip() for cell in row.findall(".//td")]
            if not cells:
                cells = ["".join(cell.itertext()).strip() for cell in row.findall(".//th")]
            rows.append(cells)
        return rows

    def _get_xml(self, publication_id: str) -> str | None:
        """Retrieve the XML content for a given publication ID.

        Args:
            publication_id (str): The ID of the publication to retrieve XML for.
        """
        if is_europepmc_id(publication_id):
            response = self._session.get(
                f"https://www.ebi.ac.uk/europepmc/webservices/rest/{publication_id}/fullTextXML",
                stream=True,
                timeout=self.timeout,
            )
            if response.ok:
                xml_path = Path(self.storage) / f"{publication_id}.xml"
                with xml_path.open("w", encoding="utf-8") as f:
                    f.write(response.text)
                tree = ET.parse(xml_path)
                Path.unlink(xml_path)
                return tree
            return None
        return None

    def _get_figures(self, publication_id: str) -> list[str]:
        """Retrieve the figure file paths for a given publication ID.

        Args:
            publication_id (str): The ID of the publication to retrieve figures for.
        """
        if zip_path := self._get_supplementary_zip_path(publication_id):
            base_dir = Path(self.figure_storage) / f"{publication_id}"
            base_dir.mkdir(parents=True, exist_ok=True)
            image_paths = []
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                for file_info in zip_ref.infolist():
                    if file_info.filename.lower().endswith(self.image_extensions):
                        zip_ref.extract(file_info, base_dir)
                        image_paths.append(str(base_dir / file_info.filename))
            Path.unlink(zip_path)
            return image_paths
        return []

    def _get_supplementary_zip_path(self, publication_id: str) -> str | None:
        """Download the supplementary files ZIP for a given publication ID and return the path to the ZIP file.

        Args:
            publication_id (str): The ID of the publication to retrieve supplementary files for.
        """
        if is_europepmc_id(publication_id):
            zip_path = Path(self.storage) / f"{publication_id}_supplementary.zip"
            response = self._session.get(
                f"https://www.ebi.ac.uk/europepmc/webservices/rest/{publication_id}/supplementaryFiles",
                stream=True,
                timeout=self.timeout,
            )
            if response.ok:
                with zip_path.open("wb") as f:
                    f.write(response.content)
                    return zip_path
        return None


def _get_publication_id(result: dict) -> str | None:
    """Extract the publication ID from the API result, checking for 'pmcid', 'pmid', and 'id' in order.

    Args:
    result (dict): The API result containing publication information.
    """
    return result.get("pmcid") or result.get("pmid") or result.get("id")
