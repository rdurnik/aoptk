from __future__ import annotations
import shutil
from pathlib import Path
import pytest
from fuzzywuzzy import fuzz
from aoptk.literature.pdf import PDF
from aoptk.literature.pymupdf_parser import PymupdfParser
from aoptk.spacy_pdf_processor import SpacyPDF

# ruff: noqa: PLR2004
# ruff: noqa: SLF001


def test_can_create(tmp_path_factory: pytest.TempPathFactoryt):
    """Can create SpacyPDF instance."""
    actual = SpacyPDF([], figure_storage=tmp_path_factory.mktemp("spacy_pdf_processor_figures"))
    assert actual is not None


def test_implements_pymupdfparser():
    """SpacyPDF implements PymupdfParser interface."""
    assert issubclass(SpacyPDF, PymupdfParser)


def test_get_publications_not_empty(tmp_path_factory: pytest.TempPathFactory):
    """Test that get_publications method returns a non-empty result."""
    actual = SpacyPDF(
        [PDF("tests/test_pdfs/test_pdf.pdf")],
        figure_storage=tmp_path_factory.mktemp("spacy_pdf_processor_figures"),
    ).get_publications()
    assert actual is not None


def test_extract_id(tmp_path_factory: pytest.TempPathFactory):
    """Test extracting publication ID from user-provided PDF."""
    parser = SpacyPDF(
        [PDF("tests/test_pdfs/test_pdf.pdf")],
        figure_storage=tmp_path_factory.mktemp("spacy_pdf_processor_figures"),
    )
    actual = parser.get_publications()[0].id
    expected = "test_pdf"
    assert str(actual) == expected
    if Path(parser.figure_storage).exists():
        shutil.rmtree(parser.figure_storage)


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
def test_is_page_header_footer(potential_footer_header: str, output: bool, tmp_path_factory: pytest.TempPathFactory):
    """Test identifying page headers and footers."""
    actual = SpacyPDF([], figure_storage=tmp_path_factory.mktemp("spacy_pdf_processor_figures"))._is_page_header_footer(
        text=potential_footer_header,
    )
    assert actual == output


@pytest.fixture(scope="module")
def publication(provide_publications: dict, provide_temp_storage_figures: dict):
    """Second stage fixture which includes PDF parsing."""
    parser = SpacyPDF(provide_publications["pdfs"], figure_storage=provide_temp_storage_figures)
    publications = parser.get_publications()
    provide_publications.update(
        {
            "publication": publications[0],
            "parser": parser,
        },
    )
    yield provide_publications

    if Path(parser.figure_storage).exists():
        shutil.rmtree(parser.figure_storage)


def test_extract_abstract_pmc(publication: dict):
    """Test extracting abstract from PMC PDFs."""
    if publication["id"] == "PMC12231352":
        pytest.skip("Spacy can't parse abstract in this paper.")
    actual = publication["publication"].abstract.text
    expected = publication["expected_abstract"]
    ratio = fuzz.ratio(actual, expected)
    assert ratio >= 35


def test_extract_figure_descriptions(publication: dict):
    """Test extracting figure descriptions from PMC PDFs."""
    actual = publication["publication"].figure_descriptions

    expected = publication["figure_descriptions"]
    ratio = fuzz.ratio(actual, expected)
    assert ratio >= 30


def test_extract_full_text_pmc(publication: dict):
    """Test extracting full text from PMC PDFs."""
    actual = " ".join(publication["publication"].full_text)
    expected = publication["full_text"]
    ratio = fuzz.ratio(actual, expected)
    assert ratio >= 50


def test_extract_tables(publication: dict):
    """Test extracting tables from PMC PDFs."""
    if publication["id"] == "PMC12181427":
        pytest.skip("SpacyPDF extracts an extra table.")
    actual = publication["publication"].tables
    expected = publication["tables"]

    assert len(actual) == expected
