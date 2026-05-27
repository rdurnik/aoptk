from __future__ import annotations
import os
from itertools import chain
from typing import Any
from Bio import Entrez
from aoptk.literature.abstract import Abstract
from aoptk.literature.databases.ncbi import NCBI
from aoptk.literature.get_abstract import GetAbstract
from aoptk.literature.get_id import GetID
from aoptk.literature.get_metadata import GetMetadata
from aoptk.literature.id import DOI
from aoptk.literature.id import ID
from aoptk.literature.id import PMCID
from aoptk.literature.id import PMID
from aoptk.literature.metadata import Metadata
from aoptk.literature.query import Query

Entrez.api_key = os.environ.get("NCBI_API_KEY")  # type: ignore[assignment]


class PubMed(GetAbstract, GetID, GetMetadata):
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

    def get_publications_metadata(self, ids: list[ID]) -> list[Metadata]:
        """Retrieve Publication metadata."""
        records = NCBI(database="pubmed").get_publications_metadata_records(ids)
        return self._parse_pubmed_metadata_records(records)

    def _parse_pubmed_metadata_records(self, records: list[list[dict[str, Any]]]) -> list[Metadata]:
        """Parse PubMed metadata records and return a list of PublicationMetadata objects.

        Args:
            records (list): A nested list containing PubMed article records.
        """
        publications_metadata: list[Metadata] = []
        for article in chain.from_iterable(records):
            pmid = article.get("Id", None)
            if pmid is None:
                continue
            pmcid = article.get("ArticleIds", {}).get("pmc", None)
            doi = article.get("DOI", None)
            if pub_date := article.get("PubDate", None):
                year = int(pub_date.split()[0])
            title = article.get("Title", None)
            authors = article.get("AuthorList", None)
            publications_metadata.append(
                Metadata(
                    id=ID(pmid),
                    pmid=PMID(pmid) if pmid else None,
                    pmcid=PMCID(pmcid) if pmcid else None,
                    doi=DOI(doi) if doi else None,
                    year=year,
                    title=title,
                    authors=authors,
                ),
            )
        return publications_metadata

    def get_ids(self) -> list[ID]:
        """Get a list of PubMed IDs from PubMed based on the query."""
        return NCBI(database="pubmed").get_ids(search_term=self.search_term)
