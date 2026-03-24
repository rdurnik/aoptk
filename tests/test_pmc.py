from __future__ import annotations
import shutil
from pathlib import Path
import pytest
from requests import HTTPError
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


@pytest.mark.xfail(raises=HTTPError)
def test_open_access_pmc_pdf_file_exists():
    """Test that an open access PMC PDF can be retrieved and saved."""
    PMC("PMC8614944").pdfs()
    filepath = Path("tests/storage") / "PMC8614944.pdf"
    assert filepath.exists()
    assert filepath.is_file()
    assert filepath.stat().st_size > 0
    shutil.rmtree("tests/storage", ignore_errors=True)


@pytest.mark.xfail(raises=HTTPError)
def test_extract_full_text(provide_publications: dict):
    """Test extracting full text."""
    actual = PMC(provide_publications["id"], figure_storage=test_figure_storage_dir).get_publications()[0].full_text
    expected = provide_publications["full_text"]
    assert actual == expected
    if Path(test_figure_storage_dir).exists():
        shutil.rmtree(test_figure_storage_dir)


@pytest.mark.xfail(raises=HTTPError)
def test_get_id_small_query():
    """Test that get_id() method returns a list of publication IDs."""
    actual = PMC("PMC12416454").id_list
    expected = ["PMC12416454"]
    assert actual == expected


@pytest.mark.xfail(raises=HTTPError)
def test_get_id_large_query():
    """Test that get_id() method returns a list of publication IDs."""
    actual = len(
        PMC("methotrexate OR thioacetamide AND cancer AND liver AND fibrosis 1940/01/01:2024/12/01[epdat]").id_list,
    )
    expected = 10129
    assert actual == expected
