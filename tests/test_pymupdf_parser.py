import os
from pathlib import Path
import pytest
from fuzzywuzzy import fuzz
from aoptk.literature.get_publication import GetPublication
from aoptk.literature.pdf import PDF
from aoptk.literature.pymupdf_parser import PymupdfParser
from aoptk.text_generation_api import TextGenerationAPI

# ruff: noqa: PLR2004
# ruff: noqa: SLF001


def test_can_create(tmp_path_factory: pytest.TempPathFactory):
    """Test that PymupdfParser can be instantiated."""
    actual = PymupdfParser(str, figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"))
    assert actual is not None


def test_implements_interface():
    """Test that PymupdfParser implements GetPublication interface."""
    assert issubclass(PymupdfParser, GetPublication)


def test_get_publication_data_not_empty(tmp_path_factory: pytest.TempPathFactory):
    """Test that get_publications method returns non-empty list."""
    actual = PymupdfParser("", figure_storage=tmp_path_factory.mktemp("pmc_storage_figures")).get_publications()
    assert actual is not None


@pytest.fixture(scope="module")
def publication(provide_publications: dict, provide_temp_storage_figures: dict):
    """Second stage fixture which includes PDF parsing."""
    parser = PymupdfParser(provide_publications["pdfs"], figure_storage=provide_temp_storage_figures)
    publications = parser.get_publications()
    provide_publications.update(
        {
            "publication": publications[0],
            "parser": parser,
        },
    )
    return provide_publications


def test_extract_abstract_pmc(publication: dict):
    """Test extracting abstract from PMC PDFs."""
    if publication["id"] == "PMC12231352":
        pytest.skip("Pymupdf can't parse abstract in this paper.")
    actual = publication["publication"].abstract.text
    expected = publication["expected_abstract"]
    ratio = fuzz.ratio(actual, expected)
    assert ratio >= 35


def test_extract_full_text_pmc(publication: dict):
    """Test extracting full text from PMC PDFs."""
    pub = publication["publication"]
    actual = pub.full_text
    expected = publication["full_text"]
    ratio = fuzz.ratio(actual, expected)
    assert ratio >= 25


def test_extract_id(tmp_path_factory: pytest.TempPathFactory):
    """Test extracting publication ID from user-provided PDF."""
    actual = (
        PymupdfParser(
            [PDF("tests/test_pdfs/test_pdf.pdf")],
            figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
        )
        .get_publications()[0]
        .id
    )
    expected = "test_pdf"
    assert str(actual) == expected


def test_extract_figure_descriptions(publication: dict):
    """Test extracting figure descriptions from PMC PDFs."""
    if publication["id"] == "PMC12181427":
        pytest.skip("Pymupdf can't parse figure captions in this paper.")

    actual = publication["publication"].figure_descriptions
    expected = publication["figure_descriptions"]
    assert actual == expected


def test_extract_figures(publication: dict):
    """Test extracting figures from PMC PDFs."""
    total_size = sum(
        Path(dirpath, filename).stat().st_size
        for dirpath, dirnames, filenames in os.walk(publication["parser"].figure_storage)
        for filename in filenames
    )
    assert len(publication["publication"].figures) == len(publication["figures"])
    assert total_size == publication["figure_size"]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("short", True),
        ("a" * 1001, False),
    ],
)
def test_is_too_short(text: str, expected: bool):
    """Test that is_too_short correctly identifies texts shorter than 1000 characters."""
    parser = PymupdfParser([])
    assert parser._is_too_short(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", False),
        ("normal text without control chars", False),
        (
            "/C84/C104/C101 /C110/C111/C110/"
            "C45/C103/C101/C110/C111/C116/C111"
            "/C120/C105/C99 /C101/C128/C101/C99"
            "/C116/C115 /C111/C102 /C116/C119/C111",
            True,
        ),
        (
            "$\t\x10\x06\x0e\t\x07 @) ,&))&. &=7A&+&\n444\x1c\x02\x15\x0f\x02\x16\x06\x02\x04",
            True,
        ),
        (
            "4\x0f\x03\x18\x06\x08\x0b\x0f\x03\x10\x03 @@ /+,,&0 @'>A@='\n...\x1c\x03\t",
            True,
        ),
    ],
)
def test_is_corrupted(text: str, expected: bool, tmp_path_factory: pytest.TempPathFactory):
    """Test that is_corrupted correctly identifies texts with excessive control characters."""
    parser = PymupdfParser([], figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"))
    assert parser._is_corrupted(text) == expected


@pytest.mark.openai
def test_extract_full_text_from_corrupted_pdf(tmp_path_factory: pytest.TempPathFactory):
    """Test extracting full text from a corrupted PDF."""
    actual = (
        PymupdfParser(
            pdfs=[PDF("tests/test_pdfs/7835547_corrupted_pdf.pdf")],
            figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
            text_generation=TextGenerationAPI(model="redhatai-scout"),
        )
        .get_publications()[0]
        .full_text
    )
    expected = (
        "Since polycyclic aromatic hydrocarbons (PAHs) are known to have epigenetic effects, "
        "we evaluated the effect of the parent chemical and the ozonated products"
    )
    assert expected in actual


def test_extract_full_text_from_corrupted_pdf_no_llm(tmp_path_factory: pytest.TempPathFactory):
    """Test extracting full text from a corrupted PDF."""
    actual = (
        PymupdfParser(
            pdfs=[PDF("tests/test_pdfs/7835547_corrupted_pdf.pdf")],
            figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
        )
        .get_publications()[0]
        .full_text
    )
    expected = ""
    assert expected == actual
