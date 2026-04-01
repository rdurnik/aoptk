from __future__ import annotations
from abc import ABC
from abc import abstractmethod


class ConvertPDFScan(ABC):
    """Abstract base class for converting PDF scans to text."""

    @abstractmethod
    def convert_pdf_scan(self, img_base64: str) -> str:
        """Return converted text data."""
        ...
