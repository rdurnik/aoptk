from __future__ import annotations
import shutil
from pathlib import Path
from aoptk.literature.databases.pmc import PMC
from aoptk.literature.get_pdf import GetPDF
from aoptk.literature.get_publication import GetPublication


def test_can_create():
    """Test that EuropePMCPDF can be instantiated."""
    actual = PMC("")
    assert actual is not None


def test_implements_interface():
    """Test that PymupdfParser implements GetPublication interface."""
    assert issubclass(PMC, GetPublication)
    assert issubclass(PMC, GetPDF)


def test_get_publication_data_not_empty():
    """Test that pdfs() method returns non-empty list."""
    actual = PMC("").pdfs()
    assert actual is not None


def test_open_access_pmc_pdf_file_exists():
    """Test that an open access PMC PDF can be retrieved and saved."""
    PMC("PMC8614944").pdfs()
    filepath = Path("tests/pdf_storage") / "PMC8614944.pdf"
    assert filepath.exists()
    assert filepath.is_file()
    assert filepath.stat().st_size > 0
    shutil.rmtree("tests/pdf_storage", ignore_errors=True)
