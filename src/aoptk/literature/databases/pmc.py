import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import boto3
import pandas as pd
from Bio import Entrez
from botocore import UNSIGNED
from botocore.client import Config
from aoptk.literature.abstract import Abstract
from aoptk.literature.databases.ncbi import NCBI
from aoptk.literature.get_abstract import GetAbstract
from aoptk.literature.get_id import GetID
from aoptk.literature.get_pdf import GetPDF
from aoptk.literature.get_publication import GetPublication
from aoptk.literature.get_publication_metadata import GetPublicationMetadata
from aoptk.literature.id import DOI
from aoptk.literature.id import ID
from aoptk.literature.id import PMCID
from aoptk.literature.id import PMID
from aoptk.literature.pdf import PDF
from aoptk.literature.publication import Publication
from aoptk.literature.publication_metadata import PublicationMetadata
from aoptk.literature.query import Query
from aoptk.literature.utils import convert_image_format
from aoptk.literature.utils import remove_pmc_prefix

Entrez.api_key = os.environ.get("NCBI_API_KEY")  # type: ignore[assignment]


class PMC(GetPublication, GetPDF, GetID, GetAbstract, GetPublicationMetadata):
    """Class to get data from PMC based on a query."""

    aws_region = "us-east-1"
    s3 = boto3.client(
        "s3",
        config=Config(signature_version=UNSIGNED),
        region_name=aws_region,
    )
    bucket = "pmc-oa-opendata"
    paginator = s3.get_paginator("list_objects_v2")

    image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff")
    unified_image_format = "png"

    def __init__(
        self,
        storage: Path,
        figure_storage: Path,
        query: Query | None = None,
    ):
        if not query:
            query = Query(search_term="queryblank")
        self.search_term = self.build_search_term(query)

        self.storage = storage
        Path(self.storage).mkdir(parents=True, exist_ok=True)

        self.figure_storage = figure_storage
        Path(self.figure_storage).mkdir(parents=True, exist_ok=True)

    def build_search_term(self, query: Query) -> str:
        """Convert Query to PMC search syntax."""
        search_term = query.search_term
        if query.full_text_subset:
            search_term += " open access[filter]"
        if query.only_preprint:
            search_term += " ahead of print[filter]"
        if query.exclude_preprint:
            search_term += " NOT ahead of print[filter]"
        if query.date:
            search_term += f" {query.date[0]}/{query.date[1]}/{query.date[2]}[dp]"
        if query.licensing:
            search_term += self._get_license_filter(query.licensing)
        return search_term

    def _get_license_filter(self, licensing: str) -> str:
        """Get the license filter string for a given licensing type.

        Args:
            licensing (str): The licensing type.

        Returns:
            str: The license filter string for PMC search.
        """
        license_map = {
            "open-access": ' "open access"[filter]',
            "CC0": ' "cc0 license"[filter]',
            "CC-BY": ' "cc by license"[filter]',
            "CC-BY-SA": ' "cc by-nc-sa license"[filter]',
            "CC-BY-ND": ' "cc by-nd license"[filter]',
            "CC-BY-NC": ' "cc by-nc license"[filter]',
            "CC-BY-NC-ND": ' "cc by-nc-nd license"[filter]',
            "CC-BY-NC-SA": ' "cc by-nc-sa license"[filter]',
        }
        return license_map.get(licensing, "")

    def get_pdfs(self, ids: list[ID]) -> list[PDF]:
        """Retrieve PDFs.

        Returns:
            list[PDF]: A list of PDF objects.
        """
        return [pdf for pdf in (self._get_pdf(publication_id) for publication_id in ids) if pdf is not None]

    def get_publications(self, ids: list[ID], download_figures_enabled: bool = True) -> list[Publication]:
        """Get a list of publications.

        Args:
            ids (list[ID]): A list of publication IDs to retrieve.
            download_figures_enabled (bool): Whether to download figures
            and include their paths in the Publication objects.

        Returns:
            list[Publication]: A list of Publication objects.
        """
        return [
            pub
            for pub in (self._get_publication(publication_id, download_figures_enabled) for publication_id in ids)
            if pub is not None
        ]

    def get_ids(self) -> list[ID]:
        """Retrieve a list of publication IDs based on the search term."""
        ids = NCBI(database="pmc").get_ids(self.search_term)
        return [ID(f"PMC{pmcid}") for pmcid in ids]

    def get_abstracts(self, ids: list[ID]) -> list[Abstract]:
        """Retrieve Abstracts based on the list of IDs."""
        records = NCBI(database="pmc").get_abstract_records(ids)
        return self._parse_pmc_abstract_records(records)

    def _parse_pmc_abstract_records(self, records: list[Any]) -> list[Abstract]:
        """Parse PMC abstract handles and return a list of Abstract objects.

        Args:
            records (list[Any]): A list of PMC Entrez fetch handles.
        """
        abstracts: list[Abstract] = []
        for record in records:
            root = ET.fromstring(record)
            for article in root.findall(".//article"):
                pmc_id = article.findtext(".//article-id")
                if not pmc_id or (abstract_node := article.find(".//abstract")) is None:
                    continue
                abstract_text = " ".join(" ".join(abstract_node.itertext()).split())
                abstracts.append(Abstract(text=abstract_text, id=ID(pmc_id)))
        return abstracts

    def get_publications_metadata(self, ids: list[ID]) -> list[PublicationMetadata]:
        """Retrieve Publication metadata.

        Args:
            ids (list[ID]): A list of publication IDs for which to retrieve metadata.
        """
        records = NCBI(database="pmc").get_publications_metadata_records(remove_pmc_prefix(ids))
        return self._parse_pmc_metadata_records(records)

    def _parse_pmc_metadata_records(self, records: list[str]) -> list[PublicationMetadata]:
        """Parse PMC metadata records and return a list of PublicationMetadata objects.

        Args:
            records (list): A list of PMC XML summary payloads.
        """
        publications_metadata: list[PublicationMetadata] = []

        for record in records:
            root = ET.fromstring(record)
            for article in root.findall(".//DocSum"):
                pmcid = article.findtext("./Item[@Name='ArticleIds']/Item[@Name='pmcid']")
                if not pmcid:
                    continue
                pmid = article.findtext("./Item[@Name='ArticleIds']/Item[@Name='pmid']")
                doi = article.findtext("./Item[@Name='ArticleIds']/Item[@Name='doi']")
                if pub_date := article.findtext("./Item[@Name='PubDate']"):
                    year = int(pub_date.split()[0])
                title = article.findtext("./Item[@Name='Title']")
                authors = [author.text for author in article.findall("./Item[@Name='AuthorList']/Item[@Name='Author']")]
                publications_metadata.append(
                    PublicationMetadata(
                        id=ID(pmcid),
                        pmcid=PMCID(pmcid),
                        pmid=PMID(pmid),
                        doi=DOI(doi),
                        year=year,
                        title=title,
                        authors=authors,
                    ),
                )
        return publications_metadata

    def _get_publication(self, publication_id: ID, download_figures_enabled: bool = True) -> Publication | None:
        """Parse a single PDF and return a Publication object.

        Args:
            publication_id (str): The publication ID to retrieve and parse.
            download_figures_enabled (bool): Whether to download figures
            and include their paths in the Publication object.
        """
        abstract = Abstract(id=publication_id, text="")

        full_text = self._get_full_text(publication_id)
        if full_text is None:
            return None

        figures = self._get_figures(publication_id) if download_figures_enabled else []
        figure_descriptions: list[str] = []
        tables: list[pd.DataFrame] = []
        return Publication(
            id=publication_id,
            abstract=abstract,
            full_text=full_text,
            figures=figures,
            figure_descriptions=figure_descriptions,
            tables=tables,
        )

    def _get_full_text(self, publication_id: ID) -> str | None:
        """Retrieve the full text for a given publication ID.

        Args:
            publication_id (str): The publication ID to retrieve the full text for.
        """
        if txt_path := self._get_file(publication_id, "txt"):
            with Path.open(txt_path, encoding="utf-8") as f:
                txt = f.read()
            Path.unlink(txt_path)
            return txt
        return None

    def _get_file(self, publication_id: ID, file_format: str) -> Path | None:
        """Retrieve the file for a given publication ID and format.

        Args:
            publication_id (str): The publication ID to retrieve the file for.
            file_format (str): The format of the file to retrieve (pdf, xml, json, or txt).
            Formats txt, xml, pdf contain full-text, while json contains metadata.
        """
        prefix = f"{publication_id}.1/{publication_id}.1.{file_format}"
        response = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=prefix, MaxKeys=1)
        if contents := response.get("Contents", []):
            if key := contents[0]["Key"]:
                filepath = Path(self.storage) / f"{publication_id}.{file_format}"
                self.s3.download_file(self.bucket, key, str(filepath))
                return filepath
            return None
        return None

    def _get_figures(self, publication_id: ID) -> list[Path]:
        """Retrieve the figure files for a given publication ID.

        Args:
            publication_id (ID): The publication ID to retrieve the figure files for.
        """
        if metadata := self._get_json(publication_id):
            supplementary_files = metadata.get("media_urls", [])
            return self._extract_figures_from_supplements(publication_id, supplementary_files)

        return []

    def _extract_figures_from_supplements(self, publication_id: ID, supplementary_files: list[str]) -> list[Path]:
        """Extract figure files from the supplementary files.

        Args:
            publication_id (ID): The publication ID to retrieve the figure files for.
            supplementary_files (list[str]): A list of supplementary file URLs to extract figures from.
        """
        figures_paths = []

        base_dir = Path(self.figure_storage) / f"{publication_id}"
        base_dir.mkdir(parents=True, exist_ok=True)

        for supplement in supplementary_files:
            parsed = urlparse(supplement)

            key = parsed.path.lstrip("/")
            if key.lower().endswith(self.image_extensions):
                image_name = Path(parsed.path).name
                image_path = base_dir / image_name
                image_path.parent.mkdir(parents=True, exist_ok=True)
                self.s3.download_file(self.bucket, key, str(image_path))
                figures_paths.append(str(image_path))
        return convert_image_format([Path(path) for path in figures_paths], self.unified_image_format)

    def _get_json(self, publication_id: ID) -> dict[str, Any] | None:
        """Retrieve the json for a given publication ID.

        Args:
            publication_id (str): The publication ID to retrieve the json for.
        """
        if json_path := self._get_file(publication_id, "json"):
            metadata = json.load(json_path.open())
            Path.unlink(json_path)
            return metadata
        return None

    def _get_pdf(self, publication_id: ID) -> PDF | None:
        """Retrieve the PDF for a given publication ID.

        Args:
            publication_id (str): The publication ID to retrieve the PDF for.
        """
        if pdf_path := self._get_file(publication_id, "pdf"):
            return PDF(pdf_path)
        return None
