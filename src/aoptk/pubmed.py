from __future__ import annotations
from metapub import PubMedFetcher
from aoptk.abstract import Abstract


class PubMed():
    """Class to get data from PubMed based on a query."""

    def __init__(self, query: str):
        self._query = query
        self.fetcher = PubMedFetcher()
        self.id_list = self.get_id_list()

    def get_abstracts(self) -> list[Abstract]:
        pass

    def get_id_list(self) -> list[str]:
        """Get a list of PubMed IDs from PubMed based on the query."""
        pmids = self.fetcher.pmids_for_query(self._query)
        return list(pmids)
    
    def get_abstract(self, pmid: str) -> Abstract:
        article = self.fetcher.article_by_pmid(pmid)

    