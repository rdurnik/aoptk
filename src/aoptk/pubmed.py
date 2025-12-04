from __future__ import annotations
from Bio import Entrez
from aoptk.abstract import Abstract
from aoptk.get_abstract import GetAbstract


class QueryTooLargeError(Exception):
    """Exception raised when query returns more than maximum_results."""

    def __init__(self, count: int, maximum: int):
        self.count = count
        self.maximum = maximum
        super().__init__(f"Query returned {count} results. Maximum allowed is {maximum - 1}.")


class PubMed(GetAbstract):
    """Class to get data from PubMed based on a query."""

    maximum_results = 10000

    def __init__(self, query: str):
        self._query = query
        self.id_list = self.get_id_list()
        self.publication_count = self.get_publication_count()
        if self.get_publication_count() >= self.maximum_results:
            raise QueryTooLargeError(self.publication_count, self.maximum_results)

    def get_abstracts(self) -> list[Abstract]:
        """Retrieve Abstracts based on the query."""
        return [
            abstract
            for abstract in (self.get_abstract(publication_id) for publication_id in self.id_list)
            if abstract is not None
        ]

    def get_publication_count(self) -> int:
        """Return the number of publications matching the query in PubMed."""
        handle = Entrez.esearch(db="pubmed", term=self._query, retmax=0)
        record = Entrez.read(handle)
        handle.close()
        return int(record.get("Count", 0))

    def get_id_list(self) -> list[str]:
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
            return Abstract(text=abstract_text, publication_id=pmid)
        return None
