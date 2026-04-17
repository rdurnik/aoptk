from __future__ import annotations
from abc import ABC
from abc import abstractmethod


class ConvertPDFScan(ABC):
    """Abstract base class for converting PDF scans to text."""

    @abstractmethod
    def convert_pdf_scan(self, image64: str, mime_type: str) -> str:
        """Return converted text data.

        Args:
            image64: Base64-encoded string of the PDF scan image.
            mime_type: MIME type of the image ('image/png').
        """
        ...
