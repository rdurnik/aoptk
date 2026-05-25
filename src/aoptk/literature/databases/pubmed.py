from __future__ import annotations
import os
from datetime import UTC
from datetime import datetime
from itertools import chain
from Bio import Entrez
from aoptk.literature.abstract import Abstract
from aoptk.literature.databases.ncbi import NCBI
from aoptk.literature.get_abstract import GetAbstract
from aoptk.literature.get_id import GetID
from aoptk.literature.get_publication_metadata import GetPublicationMetadata
from aoptk.literature.id import ID
from aoptk.literature.publication_metadata import PublicationMetadata
from aoptk.literature.query import Query

Entrez.api_key = os.environ.get("NCBI_API_KEY")  # type: ignore[assignment]


class PubMed(GetAbstract, GetID, GetPublicationMetadata):
    """Class to get data from PubMed based on a query."""

    max_retries = 5
    batch_size = 200

    def __init__(self, query: Query | None = None):
        if not query:
            query = Query(search_term="queryblank")
        self.search_term = self.build_search_term(query)

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
        records = NCBI(database="pubmed").get_abstract_records(ids)
        return self._parse_pubmed_abstract_records(records)

    def _parse_pubmed_abstract_records(self, records: list[dict]) -> list[Abstract]:
        """Parse PubMed abstract records and return a list of Abstract objects.

        Args:
            records (dict): A dictionary containing PubMed article records.
        """
        abstracts = []
        for article in chain.from_iterable(batch.get("PubmedArticle", []) for batch in records):
            pmid = ID(article["MedlineCitation"]["PMID"])
            abstract_text = "".join(article["MedlineCitation"]["Article"].get("Abstract", {}).get("AbstractText", ""))
            abstracts.append(Abstract(text=abstract_text, id=pmid))
        return abstracts

    def get_publications_metadata(self, ids: list[ID]) -> list[PublicationMetadata]:
        """Retrieve Publication metadata."""
        records = NCBI(database="pubmed").get_publications_metadata_records(ids)
        return self._parse_pubmed_metadata_records(records)

    def _parse_pubmed_metadata_records(self, records: dict[str, list]) -> list[PublicationMetadata]:
        """Parse PubMed metadata records and return a list of PublicationMetadata objects.

        Args:
            records (dict): A dictionary containing PubMed article records.
        """
        publications_metadata = []
        for record in records:
            for article in record:
                publication_id = ID(article.get("Id", "Unknown"))
                pub_date = article.get("PubDate", None)
                year_publication = pub_date.split()[0] if pub_date else "Unknown"
                title = article.get("Title", None)
                authors = ", ".join(article.get("AuthorList", []))
                search_date = datetime.now(UTC)
                publications_metadata.append(
                    PublicationMetadata(
                        id=publication_id,
                        publication_date=year_publication,
                        title=title,
                        authors=authors,
                        database="PubMed",
                        search_date=search_date,
                    ),
                )
        return publications_metadata

    def get_ids(self) -> list[ID]:
        """Get a list of PubMed IDs from PubMed based on the query."""
        return NCBI(database="pubmed").get_ids(search_term=self.search_term)
