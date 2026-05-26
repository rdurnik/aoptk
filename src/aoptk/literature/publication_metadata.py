from __future__ import annotations
from dataclasses import dataclass
from aoptk.literature.id import DOI
from aoptk.literature.id import ID
from aoptk.literature.id import PMCID
from aoptk.literature.id import PMID


@dataclass
class PublicationMetadata:
    """Data structure representing a publication.

    Attributes:
        id (ID): Identifier by which the publication was found. Can be PMID, PMCID, DOI, or other such as PPR.
        pmcid (PMCID | None): PubMed Central ID, if available.
        pmid (PMID | None): PubMed ID, if available.
        doi (DOI | None): Digital Object Identifier, if available.
        year (str | None): Year of publication.
        title (str | None): Title of the publication.
        authors (list[str] | None): Authors of the publication.
        journal (str | None): Journal in which the publication was published.
    """

    id: ID
    pmcid: PMCID | None = None
    pmid: PMID | None = None
    doi: DOI | None = None
    year: int | None = None
    title: str | None = None
    authors: list[str] | None = None
    journal: str | None = None

    def __str__(self) -> str:
        return self.title
