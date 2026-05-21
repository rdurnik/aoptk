from __future__ import annotations
import os
from datetime import UTC
from datetime import datetime
from Bio import Entrez
from aoptk.literature.abstract import Abstract
from aoptk.literature.get_abstract import GetAbstract
from aoptk.literature.get_id import GetID
from aoptk.literature.get_publication_metadata import GetPublicationMetadata
from aoptk.literature.id import ID
from aoptk.literature.publication_metadata import PublicationMetadata
from aoptk.literature.query import Query

Entrez.api_key = os.environ.get("NCBI_API_KEY")  # type: ignore[assignment]


class QueryTooLargeError(Exception):
    """Exception raised when query returns more than maximum_results."""

    def __init__(self, count: int, maximum: int):
        self.count = count
        self.maximum = maximum
        super().__init__(f"Query returned {count} results. Maximum allowed is {maximum - 1}.")


class PubMed(GetAbstract, GetID, GetPublicationMetadata):
    """Class to get data from PubMed based on a query."""

    maximum_results = 10000
    batch_size = 200
    max_retries = 5

    def __init__(self, query: Query | None = None):
        if not query:
            query = Query(search_term="queryblank")
        self.search_term = self.build_search_term(query)
        self.publication_count = self.get_publication_count()
        if self.get_publication_count() >= self.maximum_results:
            raise QueryTooLargeError(self.publication_count, self.maximum_results)

    def build_search_term(self, query: Query) -> str:
        """Convert Query to PubMed search syntax."""
        search_term = query.search_term
        if query.full_text_subset:
            search_term += " full text[sb]"
        if query.only_preprint:
            search_term += " preprint[pt]"
        if query.exclude_preprint:
            search_term += " NOT preprint[pt]"
        if query.date:
            search_term += f" {query.date[0]}/{query.date[1]}/{query.date[2]} [dp]"
        if query.licensing:
            msg = "Licensing filter is not available in PubMed."
            raise NotImplementedError(msg)
        return search_term

    def get_abstracts(self, ids: list[ID]) -> list[Abstract]:
        """Retrieve Abstracts based on the query."""
        abstracts = []
        for i in range(0, len(ids), self.batch_size):
            batch_ids = ids[i : i + self.batch_size]
            handle = Entrez.efetch(
                db="pubmed",
                id=",".join(map(str, batch_ids)),
                rettype="xml",
                max_retry=self.max_retries,
            )
            records = Entrez.read(handle)
            handle.close()
            for article in records.get("PubmedArticle", []):
                pmid = str(article["MedlineCitation"]["PMID"])
                abstract_obj = article["MedlineCitation"]["Article"].get("Abstract", {}).get("AbstractText", [])
                abstract_text = "".join(abstract_obj) if abstract_obj else ""
                abstracts.append(Abstract(text=abstract_text, id=ID(pmid)))
        return abstracts

    def get_publications_metadata(self, ids: list[ID]) -> list[PublicationMetadata]:
        """Retrieve Publication metadata."""
        publications_metadata = []
        for i in range(0, len(ids), self.batch_size):
            batch_ids = ids[i : i + self.batch_size]
            handle = Entrez.esummary(db="pubmed", id=",".join(map(str, batch_ids)), max_retry=self.max_retries)
            summary_records = Entrez.read(handle)
            handle.close()
            for summary in summary_records:
                publication_id = ID(summary.get("Id", "Unknown"))
                pub_date = summary.get("PubDate", None)
                year_publication = pub_date.split()[0] if pub_date else "Unknown"
                title = summary.get("Title", None)
                authors = ", ".join(summary.get("AuthorList", []))
                search_date = datetime.now(UTC)
            publications_metadata.append(PublicationMetadata(
                id=publication_id,
                publication_date=year_publication,
                title=title,
                authors=authors,
                database="PubMed",
                search_date=search_date,
            ))
        return publications_metadata

    def get_publication_count(self) -> int:
        """Return the number of publications."""
        handle = Entrez.esearch(db="pubmed", term=self.search_term, retmax=0)
        record = Entrez.read(handle)
        handle.close()
        return int(record.get("Count", 0))

    def get_ids(self) -> list[ID]:
        """Get a list of PubMed IDs from PubMed based on the query."""
        handle = Entrez.esearch(db="pubmed", term=self.search_term, retmax=self.maximum_results)
        record = Entrez.read(handle)
        handle.close()
        return record.get("IdList", [])
