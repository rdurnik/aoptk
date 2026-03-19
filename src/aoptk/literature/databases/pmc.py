import json
from pathlib import Path
from urllib.parse import urlparse
import boto3
from botocore import UNSIGNED
from botocore.client import Config
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.literature.get_pdf import GetPDF
from aoptk.literature.get_publication import GetPublication
from aoptk.literature.id import ID
from aoptk.literature.pdf import PDF
from aoptk.literature.publication import Publication
from aoptk.literature.utils import is_europepmc_id


class PMC(GetPublication, GetPDF):
    """Class for retrieving and parsing open access PMC publications."""

    image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff")

    s3 = boto3.client(
        "s3",
        config=Config(signature_version=UNSIGNED),
        region_name="us-east-1",
    )
    bucket = "pmc-oa-opendata"
    paginator = s3.get_paginator("list_objects_v2")

    def __init__(
        self,
        query: str,
        storage: str = "tests/storage",
        figure_storage: str = "tests/figure_storage",
    ):
        self._query = query
        ids = EuropePMC(self._query).get_id()
        self.id_list = [publication_id for publication_id in ids if publication_id and is_europepmc_id(publication_id)]

        self.storage = storage
        Path(self.storage).mkdir(parents=True, exist_ok=True)

        self.figure_storage = figure_storage
        Path(self.figure_storage).mkdir(parents=True, exist_ok=True)

    def pdfs(self) -> list[PDF]:
        """Retrieve PDFs based on the query.

        Returns:
            list[PDF]: A list of PDF objects corresponding to the publications matching the query.
        """
        return [pdf for pdf in (self._get_pdf(publication_id) for publication_id in self.id_list) if pdf is not None]

    def get_publications(self) -> list[Publication]:
        """Get a list of publications.

        Returns:
            list[Publication]: A list of Publication objects.
        """
        return [
            pub for pub in (self._get_publication(publication_id) for publication_id in self.id_list) if pub is not None
        ]

    def _get_publication(self, publication_id: str) -> Publication:
        """Parse a single PDF and return a Publication object.

        Args:
            publication_id (str): The publication ID to retrieve and parse.
        """
        publication_id = ID(publication_id)
        abstract = ""
        full_text = self._get_full_text(publication_id)
        abbreviations = {}
        figures = self._get_figures(publication_id)
        figure_descriptions = []
        tables = []
        return Publication(
            id=publication_id,
            abstract=abstract,
            full_text=full_text,
            abbreviations=abbreviations,
            figures=figures,
            figure_descriptions=figure_descriptions,
            tables=tables,
        )

    def _get_full_text(self, publication_id: str) -> str:
        """Retrieve the full text for a given publication ID.

        Args:
            publication_id (str): The publication ID to retrieve the full text for.
        """
        if txt_path := self._get_file(publication_id, "txt"):
            with Path.open(txt_path) as f:
                txt = f.read()
                Path.unlink(txt_path)
                return txt
        return None

    def _get_file(self, publication_id: str, file_format: str) -> PDF | str | None:
        """Retrieve the file for a given publication ID and format.

        Args:
            publication_id (str): The publication ID to retrieve the file for.
            file_format (str): The format of the file to retrieve (pdf, xml, json, or txt).
            Formats txt, xml, pdf contain full-text, while json contains metadata.
        """
        for page in self.paginator.paginate(
            Bucket=self.bucket,
            Prefix=f"{publication_id}.1/{publication_id}.1.{file_format}",
        ):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                filepath = Path(self.storage) / f"{publication_id}.{file_format}"
                self.s3.download_file(self.bucket, key, str(filepath))
                return filepath
        return None

    def _get_figures(self, publication_id: str) -> list[str]:
        """Retrieve the figure files for a given publication ID.

        Args:
            publication_id (str): The publication ID to retrieve the figure files for.
        """
        metadata = self._get_json(publication_id)

        supplementary_files = metadata.get("media_urls", [])
        downloaded = []

        base_dir = Path(self.storage) / f"{publication_id}"
        base_dir.mkdir(parents=True, exist_ok=True)

        for supplement in supplementary_files:
            parsed = urlparse(supplement)

            key = parsed.path.lstrip("/")
            if key.lower().endswith(self.image_extensions):
                image_name = Path(parsed.path).name
                image_path = base_dir / image_name
                image_path.parent.mkdir(parents=True, exist_ok=True)
                self.s3.download_file(self.bucket, key, str(image_path))
                downloaded.append(str(image_path))

        return downloaded

    def _get_json(self, publication_id: str) -> str:
        """Retrieve the json for a given publication ID.

        Args:
            publication_id (str): The publication ID to retrieve the json for.
        """
        if json_path := self._get_file(publication_id, "json"):
            metadata = json.load(json_path.open())
            Path.unlink(json_path)
            return metadata
        return None

    def _get_pdf(self, publication_id: str) -> PDF | None:
        """Retrieve the PDF for a given publication ID.

        Args:
            publication_id (str): The publication ID to retrieve the PDF for.
        """
        if pdf_path := self._get_file(publication_id, "pdf"):
            return PDF(pdf_path)
        return None
