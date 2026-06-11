from __future__ import annotations
import json
from pathlib import Path
import pytest
from fuzzywuzzy import fuzz
from requests import HTTPError
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.literature.get_abstract import GetAbstract
from aoptk.literature.get_id import GetID
from aoptk.literature.get_metadata import GetMetadata
from aoptk.literature.get_pdf import GetPDF
from aoptk.literature.get_publication import GetPublication
from aoptk.literature.id import DOI
from aoptk.literature.id import ID
from aoptk.literature.id import PMCID
from aoptk.literature.id import PMID
from aoptk.literature.publication import Abstract
from aoptk.literature.query import Query

# ruff: noqa: PLR2004

metadata_test = json.loads(Path("tests/test_data/europepmc_metadata.json").read_text(encoding="utf-8"))


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
    assert issubclass(EuropePMC, GetMetadata)


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
    ("ids", "expected_abstracts"),
    [
        (
            [ID("30784932")],
            [
                Abstract(
                    text=Path("tests/test_data/30784932_abstract.txt").read_text(encoding="utf-8"),
                    id=ID("30784932"),
                ),
            ],
        ),
        (
            [ID("PMC5596756")],
            [],
        ),
        (
            [ID("PMC5596756"), ID("30784932")],
            [
                Abstract(
                    text=Path("tests/test_data/30784932_abstract.txt").read_text(encoding="utf-8"),
                    id=ID("30784932"),
                ),
            ],
        ),
    ],
)
# @pytest.mark.xfail(raises=HTTPError)
def test_generate_abstracts_for_given_query(
    ids: list[ID],
    expected_abstracts: list[Abstract],
    tmp_path_factory: pytest.TempPathFactory,
):
    """Generate list of abstracts for given query."""
    abstracts = EuropePMC(
        storage=tmp_path_factory.mktemp("europepmc_storage"),
        figure_storage=tmp_path_factory.mktemp("europepmc_storage_figures"),
    ).get_abstracts(ids=ids)
    assert abstracts == expected_abstracts


@pytest.mark.parametrize(
    ("publication_ids", "test_data"),
    [
        ([ID("PMC6470827"), ID("PMC12696947")], metadata_test[0]),
        ([ID("PMC6470827"), ID("PMC12416454")], metadata_test[1]),
    ],
)
@pytest.mark.xfail(raises=HTTPError)
def test_get_publication_metadata(publication_ids: list[ID], test_data: dict, tmp_path_factory: pytest.TempPathFactory):
    """Generate publication metadata for given id."""
    publication_metadata = EuropePMC(
        storage=tmp_path_factory.mktemp("europepmc_storage"),
        figure_storage=tmp_path_factory.mktemp("europepmc_storage_figures"),
    ).get_publications_metadata(ids=publication_ids)[1]
    assert publication_metadata.year == test_data["publication_date"]
    assert publication_metadata.title == test_data["title"]
    assert publication_metadata.authors == test_data["authors"]
    assert publication_metadata.id == publication_ids[1]
    assert publication_metadata.pmcid == PMCID(test_data["pmcid"])
    assert publication_metadata.pmid == PMID(test_data["pmid"])
    assert publication_metadata.doi == DOI(test_data["doi"])


# @pytest.mark.xfail(raises=HTTPError)
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
    sut = EuropePMC(storage=provide_temp_storage, figure_storage=provide_temp_storage_figures)
    actual = sut.get_publications(ids=[provide_publications["id"]])[0].full_text

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
    sut = EuropePMC(storage=provide_temp_storage, figure_storage=provide_temp_storage_figures)
    actual = "".join(sut.get_publications(ids=[provide_publications["id"]])[0].figure_descriptions)

    expected = "".join(provide_publications["figure_descriptions"])
    ratio = fuzz.ratio(actual, expected)
    assert ratio >= 50


# @pytest.mark.xfail(raises=HTTPError)
def test_extract_figures(provide_publications: dict, provide_temp_storage: Path, provide_temp_storage_figures: Path):
    """Test extracting figures from XMLs."""
    if provide_publications["id"] == "PMC12416454":
        pytest.skip("Extra image is extracted (graphical abstract?).")

    sut = EuropePMC(storage=provide_temp_storage, figure_storage=provide_temp_storage_figures)
    actual = sut.get_publications(ids=[provide_publications["id"]])[0].figures

    expected_paths = provide_publications["figures"]
    assert len(actual) == len(expected_paths)


# @pytest.mark.xfail(raises=HTTPError)
def test_extract_tables(provide_publications: dict, provide_temp_storage: Path, provide_temp_storage_figures: Path):
    """Test extracting tables from XMLs."""
    sut = EuropePMC(storage=provide_temp_storage, figure_storage=provide_temp_storage_figures)
    actual = sut.get_publications(ids=[provide_publications["id"]])[0].tables
    expected = provide_publications["tables"]
    assert len(actual) == expected


def test_get_publications_wrong_ids_empty(tmp_path_factory: pytest.TempPathFactory):
    """Test that get_publications() method returns an empty list when given wrong IDs."""
    sut = EuropePMC(
        storage=tmp_path_factory.mktemp("pmc_storage"), figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
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


@pytest.mark.parametrize(
    ("ids", "expected_paths", "expected_number_of_pdfs"),
    [
        (
            [ID("PMC12416454"), ID("PMC8421218")],
            [
                Path("tests/test_data/PMC12416454.pdf"),
                Path("tests/test_data/PMC8421218.pdf"),
            ],
            2,
        ),
    ],
)
@pytest.mark.xfail(raises=HTTPError)
def test_pdf_file_exists(
    tmp_path_factory: pytest.TempPathFactory,
    ids: list[ID],
    expected_paths: list[Path],
    expected_number_of_pdfs: int,
):
    """Test that an open access PMC PDF can be retrieved and saved."""
    storage_dir = tmp_path_factory.mktemp("pmc_storage")
    figure_storage_dir = tmp_path_factory.mktemp("pmc_storage_figures")
    EuropePMC(storage=storage_dir, figure_storage=figure_storage_dir).get_pdfs(ids=ids)
    assert len(list(storage_dir.glob("*.pdf"))) == expected_number_of_pdfs
    for expected in expected_paths:
        filepath = storage_dir / expected.name
        assert filepath.exists()
        assert filepath.is_file()
        assert filepath.stat().st_size > 0
