import asyncio
import calendar
import datetime
from collections.abc import Callable
from typing import Any
from typing import Literal
from urllib.error import HTTPError
from Bio import Entrez
from tenacity import AsyncRetrying
from tenacity import retry_if_exception_type
from tenacity import stop_after_attempt
from tenacity import wait_random_exponential
from aoptk.literature.get_id import GetID
from aoptk.literature.id import ID
from aoptk.literature.utils import AsyncRequestLimiter


class NCBI(GetID):
    """Helper class to retrieve data from NCBI databases - PubMed and PMC."""

    Entrez.max_tries = 10
    Entrez.sleep_between_tries = 45
    max_ncbi_results = 9998
    max_concurrency = 2
    max_requests_per_second = 2
    minimal_year_publication = 1940
    datetype = "pdat"
    batch_size = 200
    async_retries = 10

    def __init__(self, database: Literal["pmc", "pubmed"]):
        self.database = database
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.limiter = AsyncRequestLimiter(self.max_requests_per_second)

    def get_ids(self, search_term: str) -> list[ID]:
        """Retrieve a list of publication IDs based on the search term."""
        return asyncio.run(self._async_get_ids(search_term))

    def get_abstract_records(self, ids: list[ID]) -> list[dict]:
        """Retrieve abstract records based on the list of IDs. Note: There is still the 10 000 records limit.

        Args:
            ids (list[ID]): A list of publication IDs for which to retrieve abstracts.
        """
        return self._batch_requests(ids=ids, func=Entrez.efetch)

    def get_publications_metadata_records(self, ids: list[ID]) -> list[Any]:
        """Retrieve publication metadata records based on the list of IDs."""
        return self._batch_requests(ids=ids, func=Entrez.esummary)

    def _batch_requests(self, ids: list[ID], func: Callable[..., Any]) -> list[Any]:
        """Helper function to batch requests to NCBI."""
        records = []
        for i in range(0, len(ids), self.batch_size):
            batch_ids = ids[i : i + self.batch_size]
            handle = func(db=self.database, id=",".join(map(str, batch_ids)))
            if self.database == "pubmed":
                records_batch = Entrez.read(handle)
            elif self.database == "pmc":
                records_batch = handle.read()
            records.append(records_batch)
            handle.close()
        return records

    async def _async_get_ids(self, search_term: str) -> list[ID]:
        """Asynchronously retrieve a list of publication IDs based on the search term."""
        count, pmc_ids = await self._async_get_publication_count_and_ids(search_term=search_term)
        if count <= self.max_ncbi_results:
            return [ID(pmcid) for pmcid in pmc_ids]

        tasks = [
            self._collect_ids_for_year(search_term=search_term, year=year)
            for year in range(self.minimal_year_publication, datetime.datetime.now(datetime.UTC).year + 1)
        ]
        yearly_results = await asyncio.gather(*tasks)

        collected_ids = [ID(pmcid) for year_ids in yearly_results for pmcid in year_ids]
        return list(set(collected_ids))

    def _get_publication_count_and_ids(
        self,
        search_term: str,
        mindate: str | None = None,
        maxdate: str | None = None,
    ) -> tuple[int, list[str]]:
        """Helper function to retrieve the count of publications and their IDs.

        Retrieves IDs and total count based on the given search term and an
        optional date range.
        """
        handle = Entrez.esearch(
            db=self.database,
            term=search_term,
            retmax=self.max_ncbi_results,
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
        search_term: str,
        mindate: str | None = None,
        maxdate: str | None = None,
    ) -> tuple[int, list[str]]:
        """Asynchronously retrieve the count of publications and their IDs based on the search term and date range."""
        async for attempt in AsyncRetrying(
            retry=retry_if_exception_type(HTTPError),
            wait=wait_random_exponential(multiplier=0.5, max=30),
            stop=stop_after_attempt(self.async_retries),
            reraise=True,
        ):
            with attempt:
                async with self.semaphore:
                    await self.limiter.wait_turn()
                    return await asyncio.to_thread(
                        self._get_publication_count_and_ids,
                        search_term=search_term,
                        mindate=mindate,
                        maxdate=maxdate,
                    )
        msg = "Unexpected control flow: retry exceeded without returning"
        raise RuntimeError(msg)

    async def _collect_ids_for_year(self, search_term: str, year: int) -> list[str]:
        """Collect publication IDs for a specific year, splitting by months and days if the count exceeds the limit."""
        year_count, year_ids = await self._async_get_publication_count_and_ids(
            search_term=search_term,
            mindate=f"{year}/01/01",
            maxdate=f"{year}/12/31",
        )
        if year_count <= self.max_ncbi_results:
            return year_ids

        return await self._collect_ids_split_by_months_days(search_term=search_term, year=year)

    async def _collect_ids_split_by_months_days(self, search_term: str, year: int) -> list[str]:
        """Collect publication IDs for a specific year.

        Split the search into months and days to avoid exceeding the result
        limit.
        """
        year_month_days_ids = []
        for month in range(1, 13):
            days_in_month = calendar.monthrange(year, month)[1]
            month_count, month_ids = await self._async_get_publication_count_and_ids(
                search_term=search_term,
                mindate=f"{year}/{month:02d}/01",
                maxdate=f"{year}/{month:02d}/{days_in_month:02d}",
            )
            if month_count <= self.max_ncbi_results:
                year_month_days_ids.extend(month_ids)
                continue

            for day in range(1, days_in_month + 1):
                _day_count, day_ids = await self._async_get_publication_count_and_ids(
                    search_term=search_term,
                    mindate=f"{year}/{month:02d}/{day:02d}",
                    maxdate=f"{year}/{month:02d}/{day:02d}",
                )
                year_month_days_ids.extend(day_ids)
        return year_month_days_ids
