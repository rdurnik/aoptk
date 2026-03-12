import os
from pathlib import Path
import pytest
from fuzzywuzzy import fuzz
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.literature.get_publication import GetPublication
from aoptk.literature.pdf import PDF
from aoptk.literature.pymupdf_parser import PymupdfParser

# ruff: noqa: PLR2004
# ruff: noqa: SLF001

output_dir = "tests/figure_storage"


def test_can_create():
    """Test that PymupdfParser can be instantiated."""
    actual = PymupdfParser(str)
    assert actual is not None


def test_implements_interface():
    """Test that PymupdfParser implements GetPublication interface."""
    assert issubclass(PymupdfParser, GetPublication)


def test_get_publication_data_not_empty():
    """Test that get_publications method returns non-empty list."""
    actual = PymupdfParser("").get_publications()
    assert actual is not None


@pytest.fixture(scope="module")
def publication(provide_pdfs: dict, tmp_path_factory: pytest.TempPathFactory):
    """Second stage fixture which includes PDF parsing."""
    parser = PymupdfParser(provide_pdfs["pdfs"], figures_output_dir=tmp_path_factory.mktemp("pymupdf_parser_figures"))
    publications = parser.get_publications()
    provide_pdfs.update(
        {
            "publication": publications[0],
            "parser": parser,
        },
    )
    return provide_pdfs


def test_extract_abstract_europepmc(publication: dict):
    """Test extracting abstract from EuropePMC PDFs."""
    actual = publication["publication"].abstract.text
    expected = publication["expected_abstract"]
    ratio = fuzz.ratio(actual, expected)
    assert ratio >= 35


def test_extract_full_text_europepmc(publication: dict):
    """Test extracting full text from EuropePMC PDFs."""
    pub = publication["publication"]
    actual = pub.full_text[publication["full_text_slice"]]
    expected = publication["full_text"]
    ratio = fuzz.ratio(actual, expected)
    assert ratio >= 20


@pytest.fixture(
    params=[
        {
            "id": "PMC12637301",
            "abbreviation_list": [
                ("A3SS", "alternative 3′ splice site"),
                ("A5SS", "alternative 5′ splice site"),
                ("WB", "Western Blot"),
            ],
        },
        {"id": "PMC12231352", "abbreviation_list": []},
        {
            "id": "PMC11339729",
            "abbreviation_list": [
                ("BEB", "binary-encounter-Bethe"),
                ("CID", "collision-induced dissociation"),
                ("UFF", "universal force field"),
            ],
        },
        {
            "id": "PMC9103499",
            "abbreviation_list": [("ABC", "ATP-binding cassette"), ("AQP", "Aquaporin"), ("VDR", "Vitamin D receptor")],
        },
        {
            "id": "PMC12577378",
            "abbreviation_list": [
                ("AD-MSCs", "Adipose mesenchymal stem cells"),
                ("AKT", "Protein kinase B"),
                ("VEGF", "Vascular endothelial growth factor"),
            ],
        },
    ],
)
def provide_params_extract_abbreviations_fixture(
    request: pytest.FixtureRequest,
    tmp_path_factory: pytest.TempPathFactory,
):
    """Provide parameters for extract abbreviations fixture."""
    europepmc = EuropePMC(request.param["id"], storage=tmp_path_factory.mktemp(f"europepmc_{request.param['id']}"))
    return {
        "europepmc": europepmc,
        "abbreviation_list": request.param["abbreviation_list"],
    }


def test_extract_abbreviations(
    provide_params_extract_abbreviations_fixture: dict,
    tmp_path_factory: pytest.TempPathFactory,
):
    """Test extracting abbreviations from EuropePMC PDFs."""
    abbrev_dict = (
        PymupdfParser(
            provide_params_extract_abbreviations_fixture["europepmc"].pdfs(),
            figures_output_dir=tmp_path_factory.mktemp("pymupdf_parser_abbreviations"),
        )
        .get_publications()[0]
        .abbreviations
    )
    expected_list = provide_params_extract_abbreviations_fixture["abbreviation_list"]

    if expected_list:
        actual = [next(iter(abbrev_dict.items())), list(abbrev_dict.items())[1], list(abbrev_dict.items())[-1]]
        assert actual == expected_list
    else:
        assert abbrev_dict == {}


def test_extract_id(tmp_path_factory: pytest.TempPathFactory):
    """Test extracting publication ID from user-provided PDF."""
    actual = (
        PymupdfParser(
            [PDF("tests/test_pdfs/test_pdf.pdf")],
            figures_output_dir=tmp_path_factory.mktemp("pymupdf_parser_extract_id"),
        )
        .get_publications()[0]
        .id
    )
    expected = "test_pdf"
    assert str(actual) == expected


def test_extract_figure_descriptions(publication: dict):
    """Test extracting figure descriptions from EuropePMC PDFs."""
    if publication["id"] == "PMC12181427":
        pytest.skip("Pymupdf can't parse figure captions in this paper.")

    actual = publication["publication"].figure_descriptions
    expected = publication["figure_descriptions"]
    assert actual == expected


def test_extract_figures(publication: dict):
    """Test extracting figures from EuropePMC PDFs."""
    actual = publication["publication"].figures
    expected = [
        str(publication["parser"].figures_output_dir / Path(fig).relative_to("tests/figure_storage"))
        for fig in publication["figures"]
    ]
    expected_size = publication["figure_size"]
    total_size = sum(
        Path(dirpath, filename).stat().st_size
        for dirpath, dirnames, filenames in os.walk(publication["parser"].figures_output_dir)
        for filename in filenames
    )
    assert actual == expected
    assert total_size == expected_size


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
def test_is_corrupted(text: str, expected: bool):
    """Test that is_corrupted correctly identifies texts with excessive control characters."""
    parser = PymupdfParser([])
    assert parser._is_corrupted(text) == expected


@pytest.mark.skipif(
    os.getenv("GITHUB_ACTIONS") == "true",
    reason="Skip in Github Actions to save energy consumption (large model download required).",
)
def test_extract_full_text_from_corrupted_pdf(tmp_path_factory: pytest.TempPathFactory):
    """Test extracting full text from a corrupted PDF."""
    actual = (
        PymupdfParser(
            pdfs=[PDF("tests/test_pdfs/7835547_corrupted_pdf.pdf")],
            figures_output_dir=tmp_path_factory.mktemp("pymupdf_parser_corrupted_pdf"),
        )
        .get_publications()[0]
        .full_text
    )
    expected = "Since polycyclic aromatic hydrocarbons (PAHs) are known to have epigenetic effects,"
    assert expected in actual
