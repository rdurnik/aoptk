from __future__ import annotations
import shutil
from datetime import UTC
from datetime import datetime
from pathlib import Path
import pytest
from fuzzywuzzy import fuzz
from requests import HTTPError
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.literature.get_abstract import GetAbstract
from aoptk.literature.get_id import GetID
from aoptk.literature.get_pdf import GetPDF
from aoptk.literature.get_publication import GetPublication

# ruff: noqa: PLR2004

test_figure_storage_dir = Path("tests/figure_storage")


def test_can_create():
    """Test that EuropePMCPDF can be instantiated."""
    actual = EuropePMC("")
    assert actual is not None


def test_implements_interface():
    """Test that PymupdfParser implements GetPublication interface."""
    assert issubclass(EuropePMC, GetPublication)
    assert issubclass(EuropePMC, GetPDF)
    assert issubclass(EuropePMC, GetAbstract)
    assert issubclass(EuropePMC, GetID)


def test_get_publication_data_not_empty():
    """Test that pdfs() method returns non-empty list."""
    actual = EuropePMC("").pdfs()
    assert actual is not None


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        (
            "liver fibrosis AND thioacetamide AND mg/kg AND weeks AND Ayurveda AND (FIRST_PDATE:[2023 TO 2024])",
            ["39705085", "PMC11420034", "PMC9962064", "PMC11059288", "PMC10829571"],
        ),
    ],
)
def test_return_id_list(query: str, expected: list[str]):
    """Test that get_id() returns expected publication IDs."""
    actual = EuropePMC(query).get_id()
    assert actual == expected


@pytest.mark.parametrize(
    ("query", "expected", "query_for_abstracts_only", "remove_reviews"),
    [
        (
            "spheroid methotrexate thioacetamide AND (FIRST_PDATE:[2021 TO 2023])",
            [
                "PMC10647544",
                "PMC9857994",
                "PMC8950395",
                "PMC8201787",
                "PMC9256002",
                "PMC7911320",
                "PMC10928813",
                "PMC10576948",
                "PMC8934723",
                "PMC9243943",
            ],
            False,
            False,
        ),
        (
            "spheroid methotrexate AND (FIRST_PDATE:[2020 TO 2021])",
            ["PMC8230402", "PMC7348038", "PMC8638776", "PPR380866", "PMC8649206", "PMC8476350", "PPR190639"],
            True,
            False,
        ),
        (
            "spheroid methotrexate hepg2 AND (FIRST_PDATE:[2024 TO 2024])",
            [
                "PMC11201042",
                "PMC11354664",
                "PMC11156946",
                "PMC12149029",
                "PMC11208286",
                "PMC11245638",
                "PMC11177578",
                "PMC11470995",
            ],
            False,
            True,
        ),
        (
            "spheroid methotrexate AND (FIRST_PDATE:[2020 TO 2024])",
            [
                "PMC11354664",
                "PPR875796",
                "39060210",
                "37454032",
                "PMC9358508",
                "PMC9434104",
                "PMC8230402",
                "PMC7348038",
                "PMC8638776",
                "PPR380866",
                "PMC8649206",
                "PMC8476350",
                "PPR190639",
            ],
            True,
            True,
        ),
    ],
)
def test_ids_not_to_return(query: str, expected: list[str], query_for_abstracts_only: bool, remove_reviews: bool):
    """Test that get_id_list() returns expected publication IDs with query modifications."""
    sut = EuropePMC(query)
    if query_for_abstracts_only:
        sut = sut.abstracts_only()
    if remove_reviews:
        sut = sut.remove_reviews()
    actual = sut.get_id()
    assert actual == expected


@pytest.mark.skip(
    reason="Europe PMC currently does not allow PDF retrieval.",
)
def test_open_access_europepmc_pdf_file_exists():
    """Test that an open access EuropePMC PDF can be retrieved and saved."""
    EuropePMC("PMC8614944").pdfs()
    filepath = Path("tests/pdf_storage") / "PMC8614944.pdf"
    assert filepath.exists()
    assert filepath.is_file()
    assert filepath.stat().st_size > 0
    shutil.rmtree("tests/pdf_storage", ignore_errors=True)


def test_get_abstract_not_empty():
    """Get abstracts returns non-empty list."""
    actual = EuropePMC("").get_abstracts()
    assert actual is not None


@pytest.mark.parametrize(
    ("query", "expected_abstract", "expected_id", "position"),
    [
        (
            "TITLE_ABS:(liver cancer AND hepg2 AND thioacetamide) AND (FIRST_PDATE:[2018 TO 2019])",
            "Insulin growth factor (IGF) family and their receptors play a great role in tumors' development. "
            "In addition, IGF-1 enhances cancer progression through regulating cell proliferation, angiogenesis, "
            "immune modulation and metastasis. Moreover, nicotinamide is association with protection against "
            "cancer. Therefore, we conducted this research to examine the therapeutic effects of nicotinamide "
            "against hepatocellular carcinoma (HCC) both in vivo and in vitro through affecting IGF-1 and "
            "the balance between PKB and Nrf2. HCC was induced in rats by 200 mg/kg, ip thioacetamide. "
            "The rat survival, number and size of tumors and serum α-fetoprotein (AFP) were measured. "
            "The gene and protein levels of IGF-1, Nrf2, PKB and JNK-MAPK were assessed in rat livers. "
            "In addition, HepG2 cells, human HCC cell lines, were treated with different concentrations "
            "of nicotinamide. We found that nicotinamide enhanced the rats' survival and reduced the "
            "number and size of hepatic tumors as well as it reduced serum AFP and HepG2 cells survival. "
            "Nicotinamide ameliorated HCC-induced reduction in the expression of Nrf2. Moreover, nicotinamide "
            "blocked HCC-induced elevation in IGF-1, PKB and JNK-MAPK. In conclusion, nicotinamide produced "
            "cytotoxic effects against HCC both in vivo and in vitro. The cytotoxic activity can be explained "
            "by inhibition of HCC-induced increased in the expression of IGF-1 and leads to disturbances "
            "in the balance between the cell death signal by PKB and MAPK; and the cell survival signal "
            "by Nrf2, directing it towards cell survival signals in normal liver cells providing more "
            "protection for body against tumor.",
            "30784932",
            0,
        ),
        (
            "PMC5596756",
            "",
            "PMC5596756",
            1,
        ),
    ],
)
@pytest.mark.xfail(raises=HTTPError)
def test_generate_abstracts_for_given_query(query: str, expected_abstract: str, expected_id: str, position: int):
    """Generate list of abstracts for given query."""
    abstract = EuropePMC(query).get_abstracts()[position].text
    publication_id = EuropePMC(query).get_abstracts()[position].publication_id
    assert abstract == expected_abstract
    assert publication_id == expected_id


@pytest.mark.parametrize(
    "test_data",
    [
        {
            "publication_id": "41345959",
            "publication_date": "2025",
            "title": "YAP-induced MAML1 cooperates with STAT3 to drive hepatocellular carcinoma progression.",
            "authors": "Li J, Li X, Wang R, Li M, Xiao Y.",
            "database": "Europe PMC",
        },
        {
            "publication_id": "40785269",
            "publication_date": "2025",
            "title": "Flexibility-Aided Orientational Self-Sorting and Transformations of Bioactive "
            "Homochiral Cuboctahedron Pd&lt;sub&gt;12&lt;/sub&gt;L&lt;sub&gt;16&lt;/sub&gt;.",
            "authors": "Chattopadhyay S, Durník R, Kiesilä A, Kalenius E, Linnanto JM, "
            "Babica P, Kuta J, Marek R, Jurček O.",
            "database": "Europe PMC",
        },
    ],
)
@pytest.mark.xfail(raises=HTTPError)
def test_get_publication_metadata(test_data: dict):
    """Generate publication metadata for given id."""
    publication_metadata = EuropePMC(test_data["publication_id"]).get_publications_metadata()[0]
    assert publication_metadata.publication_id == test_data["publication_id"]
    assert publication_metadata.publication_date == test_data["publication_date"]
    assert publication_metadata.title == test_data["title"]
    assert publication_metadata.authors == test_data["authors"]
    assert publication_metadata.database == test_data["database"]
    assert publication_metadata.search_date.year == datetime.now(UTC).year
    assert publication_metadata.search_date.month == datetime.now(UTC).month


@pytest.mark.xfail(raises=HTTPError)
def test_extract_abstract_xml(provide_publications: dict):
    """Test extracting abstract from XMLs."""
    actual = EuropePMC(provide_publications["id"]).get_publications()[0].abstract
    expected = provide_publications["expected_abstract"]
    ratio = fuzz.ratio(actual, expected)
    assert ratio >= 60
    if Path(test_figure_storage_dir).exists():
        shutil.rmtree(test_figure_storage_dir)


@pytest.mark.xfail(raises=HTTPError)
def test_extract_full_text(provide_publications: dict):
    """Test extracting full text from XMLs."""
    actual = EuropePMC(provide_publications["id"]).get_publications()[0].full_text
    expected = provide_publications["full_text"]
    ratio = fuzz.ratio(actual, expected)
    assert ratio >= 50
    if Path(test_figure_storage_dir).exists():
        shutil.rmtree(test_figure_storage_dir)


@pytest.mark.xfail(raises=HTTPError)
def test_extract_figure_descriptions(provide_publications: dict):
    """Test extracting figure descriptions from XMLs."""
    actual = "".join(EuropePMC(provide_publications["id"]).get_publications()[0].figure_descriptions)
    expected = "".join(provide_publications["figure_descriptions"])
    ratio = fuzz.ratio(actual, expected)
    assert ratio >= 50
    if Path(test_figure_storage_dir).exists():
        shutil.rmtree(test_figure_storage_dir)


@pytest.mark.xfail(raises=HTTPError)
def test_extract_figures(provide_publications: dict):
    """Test extracting figures from XMLs."""
    if provide_publications["id"] == "PMC12416454":
        pytest.skip("Extra image is extracted (graphical abstract?).")
    actual = EuropePMC(provide_publications["id"]).get_publications()[0].figures
    expected_paths = provide_publications["figures"]
    assert len(actual) == len(expected_paths)
    if Path(test_figure_storage_dir).exists():
        shutil.rmtree(test_figure_storage_dir)


@pytest.mark.xfail(raises=HTTPError)
def test_extract_tables(provide_publications: dict):
    """Test extracting tables from XMLs."""
    actual = EuropePMC(provide_publications["id"]).get_publications()[0].tables
    expected = provide_publications["tables"]
    assert len(actual) == expected
    if Path(test_figure_storage_dir).exists():
        shutil.rmtree(test_figure_storage_dir)
