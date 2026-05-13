from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

# ruff: noqa: C901
# ruff: noqa: PLR0912


@dataclass
class Query:
    """Data structure representing a query."""

    search_term: str
    database: Literal["europepmc", "pmc", "pubmed"]

    def __str__(self) -> str:
        return self.search_term

    def specify_date(self, year: int, month: int, day: int) -> Query:
        """Modify the query to include a date limit."""
        if self.database == "europepmc":
            self.search_term += f" E_PDATE:{year}/{month}/{day}"
        # self.search_term += f' E_PDATE:[{year_min}/{month_min}/{day_min} TO
        # {year_max}/{month_max}/{day_max}]' # ignore ERA001
        elif self.database == "pmc":
            self.search_term += f" {year}/{month}/{day}[dp]"
        return self

        # self.search_term += f' {year_min}/{month_min}/{day_min} TO
        # {year_max}/{month_max}/{day_max}[dp]' # ignore ERA001

    def full_text(self) -> Query:
        """Modify the query to only include articles with full text available."""
        if self.database == "europepmc":
            self.search_term += " HAS_FT:Y"
        elif self.database == "pmc":
            self.search_term += ' "open access"[filter]'
        return self

    def remove_reviews(self) -> Query:
        """Modify the query to exclude review articles."""
        if self.database == "europepmc":
            self.search_term += ' NOT PUB_TYPE:"Review"'
        elif self.database == "pmc":
            msg = "Removing reviews is not implemented for PMC database."
            raise NotImplementedError(msg)
        return self

    def preprint(self) -> Query:
        """Modify the query to include only articles that are ahead of print."""
        if self.database == "pmc":
            self.search_term += ' ahead of print"[filter]'
        elif self.database == "europepmc":
            self.search_term += " SRC:PPR"
        return self

    def search_abstract_title(self) -> Query:
        """Modify the query to search in the text of abstract and title only."""
        if self.database == "europepmc":
            self.search_term = "TITLE_ABS:(" + self.search_term + ")"
        if self.database == "pmc":
            self.search_term = self.search_term + " [tiab]"
        return self

    def licensing(self, licensing: str) -> Query:
        """Modify the query to include only articles with a license."""
        if self.database == "europepmc":
            if licensing == "open-access":
                self.search_term += " LICENSE:CC"
            if licensing == "CC0":
                self.search_term += " LICENSE:CC0"
            if licensing == "CC-BY":
                self.search_term += " LICENSE:“CC-BY”"
            if licensing == "CC-BY-SA":
                self.search_term += " LICENSE:“CC-BY-SA”"
            if licensing == "CC-BY-ND":
                self.search_term += " LICENSE:“CC-BY-ND”"
            if licensing == "CC-BY-NC":
                self.search_term += " LICENSE:“CC-BY-NC”"
            if licensing == "CC-BY-NC-ND":
                self.search_term += " LICENSE:“CC-BY-NC-ND”"
            if licensing == "CC-BY-NC-SA":
                self.search_term += " LICENSE:“CC-BY-NC-SA”"
        elif self.database == "pmc":
            if licensing == "open-access":
                self.search_term += ' "open access"[filter]'
            if licensing == "CC0":
                self.search_term += ' "cc0 license"[filter]'
            if licensing == "CC-BY":
                self.search_term += ' "cc by license"[filter]'
            if licensing == "CC-BY-SA":
                self.search_term += ' "cc by-nc-sa license"[filter]'
            if licensing == "CC-BY-ND":
                self.search_term += ' "cc by-nd license"[filter]'
            if licensing == "CC-BY-NC":
                self.search_term += ' "cc by-nc license"[filter]'
            if licensing == "CC-BY-NC-ND":
                self.search_term += ' "cc by-nc-nd license"[filter]'
            if licensing == "CC-BY-NC-SA":
                self.search_term += ' "cc by-nc-sa license"[filter]'
        return self
