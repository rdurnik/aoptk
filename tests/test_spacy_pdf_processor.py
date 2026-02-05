from __future__ import annotations
import shutil
from pathlib import Path
import pytest
from fuzzywuzzy import fuzz
from aoptk.literature.pdf import PDF
from aoptk.literature.pymupdf_parser import PymupdfParser
from aoptk.spacy_pdf_processor import SpacyPDF

# ruff: noqa: PLR2004


def test_can_create():
    """Can create SpacyPDF instance."""
    actual = SpacyPDF([])
    assert actual is not None


def test_implements_pymupdfparser():
    """SpacyPDF implements PymupdfParser interface."""
    assert issubclass(SpacyPDF, PymupdfParser)


def test_get_publications_not_empty():
    """Test that get_publications method returns a non-empty result."""
    actual = SpacyPDF([PDF("tests/test_pdfs/test_pdf.pdf")]).get_publications()
    assert actual is not None


def test_extract_id():
    """Test extracting publication ID from user-provided PDF."""
    parser = SpacyPDF([PDF("tests/test_pdfs/test_pdf.pdf")])
    actual = parser.get_publications()[0].id
    expected = "test_pdf"
    assert str(actual) == expected
    if Path(parser.figures_output_dir).exists():
        shutil.rmtree(parser.figures_output_dir)


@pytest.mark.parametrize(
    ("potential_footer_header", "output"),
    [
        (
            "doi.org/10.1002/anie.202513902",
            True,
        ),
        (
            "Durnik et al.",
            True,
        ),
        (
            "HepG2 cells were used in this study.",
            False,
        ),
    ],
)
def test_is_page_header_footer(potential_footer_header: str, output: bool):
    """Test identifying page headers and footers."""
    actual = SpacyPDF([])._is_page_header_footer(text=potential_footer_header)  # noqa: SLF001
    assert actual == output


@pytest.fixture(scope="module")
def publication(provide_pdfs: dict):
    """Second stage fixture which includes PDF parsing."""
    parser = SpacyPDF(provide_pdfs["pdfs"])
    publications = parser.get_publications()
    provide_pdfs.update(
        {
            "publication": publications[0],
            "parser": parser,
        },
    )
    yield provide_pdfs

    if Path(parser.figures_output_dir).exists():
        shutil.rmtree(parser.figures_output_dir)


def test_extract_abstract_europepmc(publication: dict):
    """Test extracting abstract from EuropePMC PDFs."""
    actual = publication["publication"].abstract.text
    expected = publication["expected_abstract"]
    ratio = fuzz.ratio(actual, expected)
    assert ratio >= 35


def test_extract_figure_descriptions(publication: dict):
    """Test extracting figure descriptions from EuropePMC PDFs."""
    actual = publication["publication"].figure_descriptions

    expected = publication["figure_descriptions"]
    ratio = fuzz.ratio(actual, expected)
    assert ratio > 50


def test_extract_full_text_europepmc(publication: dict):
    """Test extracting full text from EuropePMC PDFs."""
    actual = publication["publication"].full_text[publication["paragraph_number"]]
    expected = publication["paragraph"]
    ratio = fuzz.ratio(actual, expected)
    assert ratio > 95


def test_extract_tables(publication: dict):
    """Test extracting tables from EuropePMC PDFs."""
    actual = publication["publication"].tables
    expected = publication["tables"]

    assert len(actual) == expected
