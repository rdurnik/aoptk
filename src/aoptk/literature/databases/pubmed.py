from __future__ import annotations
import os
from datetime import datetime
from datetime import timezone
from Bio import Entrez
from aoptk.literature.abstract import Abstract
from aoptk.literature.get_abstract import GetAbstract
from aoptk.literature.get_id import GetID
from aoptk.literature.id import ID
from aoptk.literature.publication_metadata import PublicationMetadata

Entrez.api_key = os.environ.get("NCBI_API_KEY")


class QueryTooLargeError(Exception):
    """Exception raised when query returns more than maximum_results."""

    def __init__(self, count: int, maximum: int):
        self.count = count
        self.maximum = maximum
        super().__init__(f"Query returned {count} results. Maximum allowed is {maximum - 1}.")


class PubMed(GetAbstract, GetID):
    """Class to get data from PubMed based on a query."""

    maximum_results = 10000
    batch_size = 200

    def __init__(self, query: str):
        self._query = query
        self.id_list = self.get_id()
        self.publication_count = self.get_publication_count()
        if self.get_publication_count() >= self.maximum_results:
            raise QueryTooLargeError(self.publication_count, self.maximum_results)

    def get_abstracts(self) -> list[Abstract]:
        """Retrieve Abstracts based on the query."""
        abstracts = []
        for i in range(0, len(self.id_list), self.batch_size):
            batch_ids = self.id_list[i : i + self.batch_size]
            handle = Entrez.efetch(db="pubmed", id=",".join(batch_ids), rettype="xml")
            records = Entrez.read(handle)
            handle.close()
            for article in records.get("PubmedArticle", []):
                pmid = str(article["MedlineCitation"]["PMID"])
                abstract_obj = article["MedlineCitation"]["Article"].get("Abstract", {}).get("AbstractText", [])
                abstract_text = "".join(abstract_obj) if abstract_obj else ""
                abstracts.append(Abstract(text=abstract_text, publication_id=ID(pmid)))
        return abstracts

    def get_publications_metadata(self) -> list[PublicationMetadata]:
        """Retrieve Publication metadata based on the query."""
        return [
            publication_metadata
            for publication_metadata in (
                self.get_publication_metadata(publication_id) for publication_id in self.id_list
            )
            if publication_metadata is not None
        ]

    def get_publication_count(self) -> int:
        """Return the number of publications matching the query in PubMed."""
        handle = Entrez.esearch(db="pubmed", term=self._query, retmax=0)
        record = Entrez.read(handle)
        handle.close()
        return int(record.get("Count", 0))

    def get_id(self) -> list[ID]:
        """Get a list of PubMed IDs from PubMed based on the query."""
        handle = Entrez.esearch(db="pubmed", term=self._query, retmax=self.maximum_results)
        record = Entrez.read(handle)
        handle.close()
        return record.get("IdList", [])

    def get_abstract(self, pmid: str) -> Abstract:
        """Get the abstract for a given PubMed ID."""
        handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml")
        record = Entrez.read(handle)
        handle.close()
        abstract_text = ""
        if abstract_obj := record["PubmedArticle"][0]["MedlineCitation"]["Article"]["Abstract"]["AbstractText"]:
            abstract_text = "".join(abstract_obj)
            return Abstract(text=abstract_text, publication_id=ID(pmid))
        return Abstract(text="", publication_id=ID(pmid))

    def get_publication_metadata(self, pmid: str) -> PublicationMetadata:
        """Get the publication metadata for a given PubMed ID."""
        handle = Entrez.esummary(db="pubmed", id=pmid)
        summary_records = Entrez.read(handle)
        handle.close()
        for summary in summary_records:
            publication_id = pmid
            pub_date = summary.get("PubDate", None)
            year_publication = pub_date.split()[0] if pub_date else "Unknown"
            title = summary.get("Title", None)
            authors = ", ".join(summary.get("AuthorList", []))
            search_date = datetime.now(timezone.utc)
        return PublicationMetadata(
            publication_id=publication_id,
            publication_date=year_publication,
            title=title,
            authors=authors,
            database="PubMed",
            search_date=search_date,
        )
