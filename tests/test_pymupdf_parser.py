import os
import shutil
from pathlib import Path
import pytest
from fuzzywuzzy import fuzz
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.literature.get_publication import GetPublication
from aoptk.literature.pdf import PDF
from aoptk.literature.pymupdf_parser import PymupdfParser

# ruff: noqa: PLR2004

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
def publication(provide_pdfs: dict):
    """Second stage fixture which includes PDF parsing."""
    parser = PymupdfParser(provide_pdfs["pdfs"])
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
def provide_params_extract_abbreviations_fixture(request: pytest.FixtureRequest):
    """Provide parameters for extract abbreviations fixture."""
    europepmc = EuropePMC(request.param["id"])
    data = {
        "europepmc": europepmc,
        "abbreviation_list": request.param["abbreviation_list"],
    }
    yield data
    if Path(europepmc.storage).exists():
        shutil.rmtree(europepmc.storage)


def test_extract_abbreviations(provide_params_extract_abbreviations_fixture: dict):
    """Test extracting abbreviations from EuropePMC PDFs."""
    abbrev_dict = (
        PymupdfParser(provide_params_extract_abbreviations_fixture["europepmc"].pdfs())
        .get_publications()[0]
        .abbreviations
    )
    expected_list = provide_params_extract_abbreviations_fixture["abbreviation_list"]

    if expected_list:
        actual = [next(iter(abbrev_dict.items())), list(abbrev_dict.items())[1], list(abbrev_dict.items())[-1]]
        assert actual == expected_list
    else:
        assert abbrev_dict == {}
    if Path(output_dir).exists():
        shutil.rmtree(output_dir)


def test_extract_id():
    """Test extracting publication ID from user-provided PDF."""
    actual = PymupdfParser([PDF("tests/test_pdfs/test_pdf.pdf")]).get_publications()[0].id
    expected = "test_pdf"
    assert str(actual) == expected
    if Path(output_dir).exists():
        shutil.rmtree(output_dir)


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
