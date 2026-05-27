from __future__ import annotations
from dataclasses import dataclass
from aoptk.literature.id import DOI
from aoptk.literature.id import ID
from aoptk.literature.id import PMCID
from aoptk.literature.id import PMID


@dataclass
class Metadata:
    """Data structure representing a publication.

    Attributes:
        id (ID): Identifier by which the publication was found. Can be PMID, PMCID, DOI, or other such as PPR.
        pmcid (PMCID | None): PubMed Central ID, if available.
        pmid (PMID | None): PubMed ID, if available.
        doi (DOI | None): Digital Object Identifier, if available.
        year (str | None): Year of publication.
        title (str | None): Title of the publication.
        authors (list[str] | None): Authors of the publication.
    """

    id: ID
    pmcid: PMCID | None = None
    pmid: PMID | None = None
    doi: DOI | None = None
    year: int | None = None
    title: str | None = None
    authors: list[str] | None = None

    def __str__(self) -> ID:
        return self.id

    def __eq__(self, other: object) -> bool:
        """Compare Metadata by their identifiers."""
        if not isinstance(other, Metadata):
            return False
        for attr in ("id", "doi", "pmid", "pmcid"):
            a = getattr(self, attr)
            b = getattr(other, attr)
            if a is not None and b is not None and a == b:
                return True
        return False

    def __hash__(self) -> int:
        """Hash based on the identifier used by __eq__ for use in sets/dicts."""
        if self.doi is not None:
            return hash(self.doi)
        if self.pmid is not None:
            return hash(self.pmid)
        if self.pmcid is not None:
            return hash(self.pmcid)
        return hash(self.id)
