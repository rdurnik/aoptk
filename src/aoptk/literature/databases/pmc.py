import asyncio
import calendar
import datetime
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
import boto3
from Bio import Entrez
from botocore import UNSIGNED
from botocore.client import Config
from tenacity import AsyncRetrying
from tenacity import retry_if_exception_type
from tenacity import stop_after_attempt
from tenacity import wait_random_exponential
from aoptk.literature.get_id import GetID
from aoptk.literature.get_pdf import GetPDF
from aoptk.literature.get_publication import GetPublication
from aoptk.literature.id import ID
from aoptk.literature.pdf import PDF
from aoptk.literature.publication import Publication
from aoptk.literature.utils import AsyncRequestLimiter

Entrez.api_key = os.environ.get("NCBI_API_KEY")


class PMC(GetPublication, GetPDF, GetID):
    """Class for retrieving and parsing open access PMC publications."""

    aws_region = "us-east-1"
    s3 = boto3.client(
        "s3",
        config=Config(signature_version=UNSIGNED),
        region_name=aws_region,
    )
    bucket = "pmc-oa-opendata"
    paginator = s3.get_paginator("list_objects_v2")

    max_pmc_results = 9998
    max_concurrency = 2
    max_requests_per_second = 2.0
    minimal_year_publication = 1800
    semaphore = asyncio.Semaphore(max_concurrency)
    limiter = AsyncRequestLimiter(max_requests_per_second)
    retries = 5
    image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff")

    def __init__(
        self,
        query: str,
        storage: str,
        figure_storage: str,
    ):
        self._query = query
        self.id_list = asyncio.run(self.get_ids())

        self.storage = storage
        Path(self.storage).mkdir(parents=True, exist_ok=True)

        self.figure_storage = figure_storage
        Path(self.figure_storage).mkdir(parents=True, exist_ok=True)

    def get_pdfs(self) -> list[PDF]:
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

    async def get_ids(self) -> list[ID]:
        """Retrieve a list of publication IDs based on the query."""
        count, ids = await self._async_get_publication_count_and_ids()
        if count <= self.max_pmc_results:
            return [f"PMC{pmcid}" for pmcid in ids]

        tasks = [
            self._collect_ids_for_year(year)
            for year in range(self.minimal_year_publication, datetime.datetime.now(datetime.UTC).year + 1)
        ]
        yearly_results = await asyncio.gather(*tasks)

        ids = [f"PMC{pmcid}" for year_ids in yearly_results for pmcid in year_ids]
        return list(set(ids))

    def _get_publication(self, publication_id: str) -> Publication:
        """Parse a single PDF and return a Publication object.

        Args:
            publication_id (str): The publication ID to retrieve and parse.
        """
        publication_id = ID(publication_id)
        abstract = ""
        full_text = self._get_full_text(publication_id)
        figures = self._get_figures(publication_id)
        figure_descriptions = []
        tables = []
        return Publication(
            id=publication_id,
            abstract=abstract,
            full_text=full_text,
            figures=figures,
            figure_descriptions=figure_descriptions,
            tables=tables,
        )

    def _get_full_text(self, publication_id: str) -> str | None:
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
        if metadata := self._get_json(publication_id):
            supplementary_files = metadata.get("media_urls", [])
            return self._extract_figures_from_supplements(publication_id, supplementary_files)

        return []

    def _extract_figures_from_supplements(self, publication_id: str, supplementary_files: list[str]) -> list[str]:
        """Extract figure files from the supplementary files.

        Args:
            publication_id (str): The publication ID to retrieve the figure files for.
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
        return figures_paths

    def _get_json(self, publication_id: str) -> str | None:
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

    def _get_publication_count_and_ids(
        self,
        mindate: str | None = None,
        maxdate: str | None = None,
    ) -> tuple[int, list[str]]:
        handle = Entrez.esearch(
            db="pmc",
            term=self._query,
            retmax=self.max_pmc_results,
            mindate=mindate,
            maxdate=maxdate,
            datetype="pdat",
        )
        record = Entrez.read(handle)
        handle.close()
        count = int(record.get("Count", 0))
        ids = record.get("IdList", [])
        return count, ids

    async def _async_get_publication_count_and_ids(
        self,
        mindate: str | None = None,
        maxdate: str | None = None,
    ) -> tuple[int, list[str]] | None:
        async for attempt in AsyncRetrying(
            retry=retry_if_exception_type(HTTPError),
            wait=wait_random_exponential(multiplier=0.5, max=30),
            stop=stop_after_attempt(self.retries),
            reraise=True,
        ):
            with attempt:
                async with self.semaphore:
                    await self.limiter.wait_turn()
                    return await asyncio.to_thread(
                        self._get_publication_count_and_ids,
                        mindate,
                        maxdate,
                    )
        return None

    async def _collect_ids_for_year(self, year: int) -> list[str]:
        year_count, year_ids = await self._async_get_publication_count_and_ids(
            mindate=f"{year}/01/01",
            maxdate=f"{year}/12/31",
        )
        if year_count <= self.max_pmc_results:
            return year_ids

        return await self._collect_ids_split_by_months_days(year)

    async def _collect_ids_split_by_months_days(self, year: int) -> list[str]:
        year_month_days_ids = []
        for month in range(1, 13):
            days_in_month = calendar.monthrange(year, month)[1]
            month_count, month_ids = await self._async_get_publication_count_and_ids(
                mindate=f"{year}/{month:02d}/01",
                maxdate=f"{year}/{month:02d}/{days_in_month:02d}",
            )
            if month_count <= self.max_pmc_results:
                year_month_days_ids.extend(month_ids)
                continue

            for day in range(1, days_in_month + 1):
                _day_count, day_ids = await self._async_get_publication_count_and_ids(
                    mindate=f"{year}/{month:02d}/{day:02d}",
                    maxdate=f"{year}/{month:02d}/{day:02d}",
                )
                year_month_days_ids.extend(day_ids)
        return year_month_days_ids
