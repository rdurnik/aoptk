import asyncio
import calendar
import datetime
from typing import Literal
from urllib.error import HTTPError
from Bio import Entrez
from tenacity import AsyncRetrying
from tenacity import retry_if_exception_type
from tenacity import stop_after_attempt
from tenacity import wait_random_exponential
from aoptk.literature.id import ID
from aoptk.literature.utils import AsyncRequestLimiter
from aoptk.literature.get_id import GetID


class NCBI(GetID):
    """Helper class to retrieve data from NCBI databases - PubMed and PMC."""

    max_pmc_results = 9998
    max_concurrency = 2
    max_requests_per_second = 2
    minimal_year_publication = 1940
    semaphore = asyncio.Semaphore(max_concurrency)
    limiter = AsyncRequestLimiter(max_requests_per_second)
    retries = 5
    datetype = "pdat"
    batch_size = 200
    max_retries = 5

    def __init__(self, search_term, database: Literal["pmc", "pubmed"]):
        self.database = database
        self.search_term = search_term

    def get_ids(self) -> list[ID]:
        """Retrieve a list of publication IDs based on the search term."""
        return asyncio.run(self._async_get_ids())
    
    def get_abstract_records(self, ids: list[ID]) -> dict[str, list]:
        """Retrieve abstract records based on the list of IDs."""
        records: dict[str, list] = {"PubmedArticle": []}
        for i in range(0, len(ids), self.batch_size):
            batch_ids = ids[i : i + self.batch_size]
            handle = Entrez.efetch(
                db=self.database,
                id=",".join(map(str, batch_ids)),
                rettype="xml",
                max_retry=self.max_retries,
            )
            records_batch = Entrez.read(handle)
            records["PubmedArticle"].extend(records_batch.get("PubmedArticle", []))
            handle.close()
        return records
    
    def get_publications_metadata_records(self, ids: list[ID]) -> dict[str, list]:
        """Retrieve abstract records based on the list of IDs."""
        records: dict[str, list] = {"PubmedArticle": []}
        for i in range(0, len(ids), self.batch_size):
            batch_ids = ids[i : i + self.batch_size]
            handle = Entrez.esummary(db=self.database, id=",".join(map(str, batch_ids)), max_retry=self.max_retries)
            records_batch = Entrez.read(handle)
            records["PubmedArticle"].extend(records_batch)
            handle.close()
        return records

    async def _async_get_ids(self) -> list[ID]:
        """Asynchronously retrieve a list of publication IDs based on the search term."""
        count, pmc_ids = await self._async_get_publication_count_and_ids()
        if count <= self.max_pmc_results:
            return [ID(pmcid) for pmcid in pmc_ids]

        tasks = [
            self._collect_ids_for_year(year)
            for year in range(self.minimal_year_publication, datetime.datetime.now(datetime.UTC).year + 1)
        ]
        yearly_results = await asyncio.gather(*tasks)

        collected_ids = [ID(pmcid) for year_ids in yearly_results for pmcid in year_ids]
        return list(set(collected_ids))

    def _get_publication_count_and_ids(
        self,
        mindate: str | None = None,
        maxdate: str | None = None,
    ) -> tuple[int, list[str]]:
        handle = Entrez.esearch(
            db=self.database,
            term=self.search_term,
            retmax=self.max_pmc_results,
            mindate=mindate,
            maxdate=maxdate,
            datetype=self.datetype,
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
    ) -> tuple[int, list[str]]:
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
        msg = "Unexpected control flow: retry exceeded without returning"
        raise RuntimeError(msg)

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
