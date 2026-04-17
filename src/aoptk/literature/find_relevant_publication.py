from __future__ import annotations
from abc import ABC
from abc import abstractmethod


class FindRelevantPublication(ABC):
    """Abstract base class for finding relevant publications."""

    @abstractmethod
    def find_relevant_publications(self, question: str, text: str) -> str:
        """Return a list of relevant publications based on the query.

        Args:
            question: Yes/No question about the publication.
            text: Extracted text of the publication.
        """
        ...
