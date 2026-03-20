from __future__ import annotations
import shutil
from pathlib import Path
import pytest
from aoptk.literature.databases.pmc import PMC
from aoptk.literature.get_pdf import GetPDF
from aoptk.literature.get_publication import GetPublication

test_figure_storage_dir = "tests/figure_storage"


def test_can_create():
    """Test that EuropePMCPDF can be instantiated."""
    actual = PMC("PMC8614944")
    assert actual is not None


def test_implements_interface():
    """Test that PymupdfParser implements GetPublication interface."""
    assert issubclass(PMC, GetPublication)
    assert issubclass(PMC, GetPDF)


def test_get_publication_data_not_empty():
    """Test that pdfs() method returns non-empty list."""
    actual = PMC("PMC8614944").pdfs()
    assert actual is not None


def test_open_access_pmc_pdf_file_exists():
    """Test that an open access PMC PDF can be retrieved and saved."""
    PMC("PMC8614944").pdfs()
    filepath = Path("tests/storage") / "PMC8614944.pdf"
    assert filepath.exists()
    assert filepath.is_file()
    assert filepath.stat().st_size > 0
    shutil.rmtree("tests/storage", ignore_errors=True)


@pytest.mark.parametrize(
    ("query", "full_text_path", "images_number"),
    [
        ("PMC12416454", "tests/test-data/PMC12416454.txt", 6),
    ],
)
def test_full_text_extraction(query: str, full_text_path: str, images_number: int):
    """Test that full text can be extracted from an open access PMC PDF."""
    actual = PMC(query, figure_storage=test_figure_storage_dir).get_publications()
    with Path.open(full_text_path) as f:
        expected_full_text = f.read()
    assert actual[0].full_text == expected_full_text
    assert len(actual[0].figures) == images_number
    shutil.rmtree(test_figure_storage_dir, ignore_errors=True)


def test_get_id_small_query():
    """Test that get_id() method returns a list of publication IDs."""
    actual = PMC("PMC12416454").id_list
    expected = ["PMC12416454"]
    assert actual == expected


def test_get_id_large_query():
    """Test that get_id() method returns a list of publication IDs."""
    actual = len(PMC("mouse AND methotrexate OR thioacetamide AND cancer AND liver AND fibrosis").id_list)
    expected = 11439
    assert actual == expected
