from __future__ import annotations
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
from aoptk.literature.get_publication_metadata import GetPublicationMetadata
from aoptk.literature.id import ID
from aoptk.literature.query import Query

# ruff: noqa: PLR2004


def test_can_create(tmp_path_factory: pytest.TempPathFactory):
    """Test that EuropePMCPDF can be instantiated."""
    actual = EuropePMC(
        storage=tmp_path_factory.mktemp("europepmc_storage"),
        figure_storage=tmp_path_factory.mktemp("europepmc_storage_figures"),
    )
    assert actual is not None


def test_implements_interface():
    """Test that PymupdfParser implements GetPublication interface."""
    assert issubclass(EuropePMC, GetPublication)
    assert issubclass(EuropePMC, GetPDF)
    assert issubclass(EuropePMC, GetAbstract)
    assert issubclass(EuropePMC, GetID)
    assert issubclass(EuropePMC, GetPublicationMetadata)


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        (
            Query(
                search_term=(
                    "liver fibrosis AND thioacetamide AND mg/kg AND weeks AND Ayurveda AND (FIRST_PDATE:[2023 TO 2024])"
                ),
            ),
            ["39705085", "PMC11420034", "PMC9962064", "PMC11059288", "PMC10829571"],
        ),
    ],
)
def test_return_id_list(
    query: Query,
    expected: list[str],
    tmp_path_factory: pytest.TempPathFactory,
):
    """Test that get_id() returns expected publication IDs."""
    actual = EuropePMC(
        query=query,
        storage=tmp_path_factory.mktemp("europepmc_storage"),
        figure_storage=tmp_path_factory.mktemp("europepmc_storage_figures"),
    ).get_ids()
    assert actual == expected


def test_get_abstract_not_empty(tmp_path_factory: pytest.TempPathFactory):
    """Get abstracts returns non-empty list."""
    actual = EuropePMC(
        storage=tmp_path_factory.mktemp("europepmc_storage"),
        figure_storage=tmp_path_factory.mktemp("europepmc_storage_figures"),
    ).get_abstracts(
        ids=[],
    )
    assert actual is not None


@pytest.mark.parametrize(
    ("query", "expected_abstract", "expected_id", "position"),
    [
        (
            Query(search_term="TITLE_ABS:(liver cancer AND hepg2 AND thioacetamide) AND (FIRST_PDATE:[2018 TO 2019])"),
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
            Query(search_term="PMC5596756"),
            "",
            "PMC5596756",
            1,
        ),
    ],
)
@pytest.mark.xfail(raises=HTTPError)
def test_generate_abstracts_for_given_query(
    query: Query,
    expected_abstract: str,
    expected_id: str,
    position: int,
    tmp_path_factory: pytest.TempPathFactory,
):
    """Generate list of abstracts for given query."""
    ids = EuropePMC(
        query=query,
        storage=tmp_path_factory.mktemp("europepmc_storage"),
        figure_storage=tmp_path_factory.mktemp("europepmc_storage_figures"),
    ).get_ids()
    abstract = (
        EuropePMC(
            query=query,
            storage=tmp_path_factory.mktemp("europepmc_storage"),
            figure_storage=tmp_path_factory.mktemp("europepmc_storage_figures"),
        )
        .get_abstracts(ids=ids)[position]
        .text
    )
    publication_id = (
        EuropePMC(
            query=query,
            storage=tmp_path_factory.mktemp("europepmc_storage"),
            figure_storage=tmp_path_factory.mktemp("europepmc_storage_figures"),
        )
        .get_abstracts(ids=ids)[position]
        .id
    )
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
def test_get_publication_metadata(test_data: dict, tmp_path_factory: pytest.TempPathFactory):
    """Generate publication metadata for given id."""
    publication_metadata = EuropePMC(
        storage=tmp_path_factory.mktemp("europepmc_storage"),
        figure_storage=tmp_path_factory.mktemp("europepmc_storage_figures"),
    ).get_publications_metadata(ids=[test_data["publication_id"]])[0]
    assert publication_metadata.id == test_data["publication_id"]
    assert publication_metadata.publication_date == test_data["publication_date"]
    assert publication_metadata.title == test_data["title"]
    assert publication_metadata.authors == test_data["authors"]
    assert publication_metadata.database == test_data["database"]
    assert publication_metadata.search_date.year == datetime.now(UTC).year
    assert publication_metadata.search_date.month == datetime.now(UTC).month


@pytest.mark.xfail(raises=HTTPError)
def test_extract_abstract_xml(
    provide_publications: dict,
    provide_temp_storage: Path,
    provide_temp_storage_figures: Path,
):
    """Test extracting abstract from XMLs."""
    actual = (
        EuropePMC(storage=provide_temp_storage, figure_storage=provide_temp_storage_figures)
        .get_publications(ids=[provide_publications["id"]])[0]
        .abstract.text
    )
    expected = provide_publications["expected_abstract"]
    ratio = fuzz.ratio(actual, expected)
    assert ratio >= 60


@pytest.mark.xfail(raises=HTTPError)
def test_extract_full_text(provide_publications: dict, provide_temp_storage: Path, provide_temp_storage_figures: Path):
    """Test extracting full text from XMLs."""
    actual = (
        EuropePMC(storage=provide_temp_storage, figure_storage=provide_temp_storage_figures)
        .get_publications(ids=[provide_publications["id"]])[0]
        .full_text
    )
    expected = provide_publications["full_text"]
    ratio = fuzz.ratio(actual, expected)
    assert ratio >= 50


@pytest.mark.xfail(raises=HTTPError)
def test_extract_figure_descriptions(
    provide_publications: dict,
    provide_temp_storage: Path,
    provide_temp_storage_figures: Path,
):
    """Test extracting figure descriptions from XMLs."""
    actual = "".join(
        EuropePMC(storage=provide_temp_storage, figure_storage=provide_temp_storage_figures)
        .get_publications(ids=[provide_publications["id"]])[0]
        .figure_descriptions,
    )
    expected = "".join(provide_publications["figure_descriptions"])
    ratio = fuzz.ratio(actual, expected)
    assert ratio >= 50


@pytest.mark.xfail(raises=HTTPError)
def test_extract_figures(provide_publications: dict, provide_temp_storage: Path, provide_temp_storage_figures: Path):
    """Test extracting figures from XMLs."""
    if provide_publications["id"] == "PMC12416454":
        pytest.skip("Extra image is extracted (graphical abstract?).")
    actual = (
        EuropePMC(storage=provide_temp_storage, figure_storage=provide_temp_storage_figures)
        .get_publications(ids=[provide_publications["id"]])[0]
        .figures
    )
    expected_paths = provide_publications["figures"]
    assert len(actual) == len(expected_paths)


@pytest.mark.xfail(raises=HTTPError)
def test_extract_tables(provide_publications: dict, provide_temp_storage: Path, provide_temp_storage_figures: Path):
    """Test extracting tables from XMLs."""
    actual = (
        EuropePMC(storage=provide_temp_storage, figure_storage=provide_temp_storage_figures)
        .get_publications(ids=[provide_publications["id"]])[0]
        .tables
    )
    expected = provide_publications["tables"]
    assert len(actual) == expected


def test_get_publications_wrong_ids_empty(tmp_path_factory: pytest.TempPathFactory):
    """Test that get_publications() method returns an empty list when given wrong IDs."""
    sut = EuropePMC(
        storage=tmp_path_factory.mktemp("pmc_storage"),
        figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
    )

    actual = sut.get_publications([ID("invalid_id")])
    assert actual == []


@pytest.mark.xfail(raises=HTTPError)
def test_figures_not_being_downloaded(
    provide_publications: dict,
    provide_temp_storage: Path,
    provide_temp_storage_figures: Path,
):
    """Test extracting figures from XMLs."""
    actual = (
        EuropePMC(storage=provide_temp_storage, figure_storage=provide_temp_storage_figures)
        .get_publications(ids=[provide_publications["id"]], download_figures_enabled=False)[0]
        .figures
    )
    expected: list = []
    assert actual == expected


@pytest.mark.parametrize(
    ("query", "ids_to_return", "ids_not_to_return"),
    [
        (
            Query(
                search_term=("liver fibrosis"),
                date=("2023", "01", "30"),
            ),
            ["PMC9922852", "PMC9922741", "PMC10392122"],
            ["PMC7322594", "PMC7589994", "PMC7073061"],
        ),
        (
            Query(
                search_term=("liver fibrosis hepg2 spheroid"),
                full_text_subset=True,
            ),
            ["PMC12423616", "PMC12225867", "PMC12214119"],
            ["38740170", "39889902"],
        ),
        (
            Query(
                search_term=("methotrexate thioacetamide"),
                licensing="CC-BY-NC-ND",
            ),
            ["PMC11926359", "PMC8851638", "PMC8240184"],
            ["PMC12755308", "PMC12472545", "PMC11420034"],
        ),
        (
            Query(search_term=("cancer"), full_text_subset=True, date=("2024", "04", "02"), licensing="CC-BY-NC-SA"),
            ["PMC10986815", "PMC10986814", "PMC10988649"],
            ["PMC11202350", "PMC11470834", "PMC11177894"],
        ),
        (
            Query(
                search_term=("methotrexate thioacetamide"),
                exclude_preprint=True,
            ),
            ["39648422", "PMC11739078", "PMC12999293"],
            [],
        ),
    ],
)
@pytest.mark.xfail(raises=HTTPError)
def test_query_filtering(
    tmp_path_factory: pytest.TempPathFactory,
    query: Query,
    ids_to_return: list[str],
    ids_not_to_return: list[str],
):
    """Test that the query filters results correctly."""
    sut = EuropePMC(
        query=query,
        storage=tmp_path_factory.mktemp("pmc_storage"),
        figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
    )
    actual_ids = sut.get_ids()
    for publication_id in ids_to_return:
        assert publication_id in actual_ids
    for publication_id in ids_not_to_return:
        assert publication_id not in actual_ids


@pytest.mark.xfail(raises=HTTPError)
def test_preprint_filtering(tmp_path_factory: pytest.TempPathFactory):
    """Test that the preprint filter works correctly."""
    sut = EuropePMC(
        query=Query(
            search_term="liver cancer hepg2",
            only_preprint=True,
        ),
        storage=tmp_path_factory.mktemp("pmc_storage"),
        figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
    )
    actual_ids = sut.get_ids()
    approx_number_of_preprints = 10000
    assert len(actual_ids) < approx_number_of_preprints


@pytest.mark.xfail(raises=HTTPError)
def test_exclude_only_preprint(tmp_path_factory: pytest.TempPathFactory):
    """Test that the preprint filter works correctly."""
    sut = EuropePMC(
        query=Query(
            search_term="liver cancer",
            only_preprint=True,
            exclude_preprint=True,
        ),
        storage=tmp_path_factory.mktemp("pmc_storage"),
        figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
    )
    actual_ids = sut.get_ids()
    assert len(actual_ids) == 0
