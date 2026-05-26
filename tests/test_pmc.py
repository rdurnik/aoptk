from __future__ import annotations
import json
from http.client import RemoteDisconnected
from pathlib import Path
import pytest
from fuzzywuzzy import fuzz
from requests import HTTPError
from aoptk.literature.databases.pmc import PMC
from aoptk.literature.get_abstract import GetAbstract
from aoptk.literature.get_pdf import GetPDF
from aoptk.literature.get_publication import GetPublication
from aoptk.literature.get_publication_metadata import GetPublicationMetadata
from aoptk.literature.id import DOI
from aoptk.literature.id import ID
from aoptk.literature.id import PMCID
from aoptk.literature.id import PMID
from aoptk.literature.query import Query

# ruff: noqa: PLR2004

metadata_test = json.loads(Path("tests/test-data/ncbi_metadata.json").read_text(encoding="utf-8"))


def test_can_create(tmp_path_factory: pytest.TempPathFactory):
    """Test that PMC can be instantiated."""
    actual = PMC(
        storage=tmp_path_factory.mktemp("pmc_storage"),
        figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
    )
    assert actual is not None


def test_implements_interface():
    """Test that PMC implements interfaces."""
    assert issubclass(PMC, GetPublication)
    assert issubclass(PMC, GetPDF)
    assert issubclass(PMC, GetAbstract)
    assert issubclass(PMC, GetPublicationMetadata)


def test_get_publication_data_not_empty(tmp_path_factory: pytest.TempPathFactory):
    """Test that pdfs() method returns non-empty list."""
    actual = PMC(
        query=Query(search_term="PMC8614944"),
        storage=tmp_path_factory.mktemp("pmc_storage"),
        figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
    ).get_pdfs(ids=[])
    assert actual is not None


@pytest.mark.xfail(raises=HTTPError)
def test_open_access_pmc_pdf_file_exists(tmp_path_factory: pytest.TempPathFactory):
    """Test that an open access PMC PDF can be retrieved and saved."""
    storage_dir = tmp_path_factory.mktemp("pmc_storage")
    figure_storage_dir = tmp_path_factory.mktemp("pmc_storage_figures")
    PMC(storage=storage_dir, figure_storage=figure_storage_dir).get_pdfs(ids=[ID("PMC8614944")])
    filepath = storage_dir / "PMC8614944.pdf"
    assert filepath.exists()
    assert filepath.is_file()
    assert filepath.stat().st_size > 0


@pytest.mark.xfail(raises=HTTPError)
def test_extract_full_text(provide_publications: dict, provide_temp_storage: Path, provide_temp_storage_figures: Path):
    """Test extracting full text."""
    actual = (
        PMC(storage=provide_temp_storage, figure_storage=provide_temp_storage_figures)
        .get_publications(ids=[provide_publications["id"]])[0]
        .full_text
    )
    expected = provide_publications["full_text"]
    assert actual == expected


@pytest.mark.xfail(raises=HTTPError)
def test_get_id_small_query(tmp_path_factory: pytest.TempPathFactory):
    """Test that get_id() method returns a list of publication IDs."""
    actual = PMC(
        query=Query(search_term="PMC12416454"),
        storage=tmp_path_factory.mktemp("pmc_storage"),
        figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
    ).get_ids()
    expected = ["PMC12416454"]
    assert actual == expected


@pytest.mark.xfail(raises=(HTTPError, RemoteDisconnected))
def test_get_id_large_query(tmp_path_factory: pytest.TempPathFactory):
    """Test that get_id() method returns a list of publication IDs."""
    actual = len(
        PMC(
            query=Query(
                search_term="methotrexate OR thioacetamide AND cancer AND fibrosis 1940/01/01:2023/01/30[epdat]",
            ),
            storage=tmp_path_factory.mktemp("pmc_storage"),
            figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
        ).get_ids(),
    )
    expected = 10101
    assert actual == pytest.approx(expected, abs=100)


@pytest.mark.xfail(raises=HTTPError)
def test_get_publications_wrong_ids_empty(tmp_path_factory: pytest.TempPathFactory):
    """Test that get_publications() method returns an empty list when given wrong IDs."""
    sut = PMC(
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
    """Test that figures are not downloaded when download_figures_enabled is False."""
    actual = (
        PMC(storage=provide_temp_storage, figure_storage=provide_temp_storage_figures)
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
            ["PMC9922831", "PMC9952723", "PMC9923003"],
            ["PMC8941514", "PMC12813988", "PMC5116602"],
        ),
        (
            Query(
                search_term=("liver fibrosis hepg2 spheroid"),
                full_text_subset=True,
            ),
            ["PMC12134770", "PMC11942424", "PMC6833180"],
            ["PMC12209135", "PMC11151446", "PMC1858558"],
        ),
        (
            Query(
                search_term=("methotrexate thioacetamide"),
                licensing="CC-BY-NC-ND",
            ),
            ["PMC8864607", "PMC11926359", "PMC10184048"],
            ["PMC5493342", "PMC13094394", "PMC8934723"],
        ),
        (
            Query(search_term=("cancer"), full_text_subset=True, date=("2024", "04", "02"), licensing="CC-BY-NC-SA"),
            ["PMC10986815", "PMC10988649", "PMC10986814"],
            ["PMC11202350", "PMC11470834", "PMC11177894"],
        ),
        (
            Query(
                search_term=("methotrexate thioacetamide"),
                exclude_preprint=True,
            ),
            ["PMC5493342", "PMC10224822", "PMC2096525"],
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
    sut = PMC(
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
    sut = PMC(
        query=Query(
            search_term="liver cancer",
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
    sut = PMC(
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
    ("ids", "expected_abstracts"),
    [
        (
            [ID("PMC12231352"), ID("PMC12416454")],
            (Path("tests/test-data/PMC12416454_abstract.txt").read_text(encoding="utf-8")),
        ),
    ],
)
@pytest.mark.xfail(raises=HTTPError)
def test_generate_abstracts_for_specific_publications(
    ids: list[ID],
    expected_abstracts: list[str],
    tmp_path_factory: pytest.TempPathFactory,
):
    """Generate list of abstracts for given query."""
    abstract = PMC(
        storage=tmp_path_factory.mktemp("pmc_storage"),
        figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
    ).get_abstracts(ids=ids)[1]
    ratio = fuzz.ratio(abstract.text, expected_abstracts)
    assert ratio >= 75


def test_generate_abstracts_multiple_abstracts(
    tmp_path_factory: pytest.TempPathFactory,
):
    """Generate list of abstracts for given query."""
    ids = PMC(
        query=Query(search_term="thioacetamide liver fibrosis cancer methotrexate"),
        storage=tmp_path_factory.mktemp("pmc_storage"),
        figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
    ).get_ids()
    abstracts = PMC(
        storage=tmp_path_factory.mktemp("pmc_storage"),
        figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
    ).get_abstracts(ids=ids)
    minimal_number_of_expected_abstracts = 300
    assert len(abstracts) > minimal_number_of_expected_abstracts


def test_generate_metadata_multiple_publications(tmp_path_factory: pytest.TempPathFactory):
    """Generate list of publication metadata for given query."""
    ids = PMC(
        query=Query(search_term="thioacetamide liver fibrosis methotrexate"),
        storage=tmp_path_factory.mktemp("pmc_storage"),
        figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
    ).get_ids()
    metadata = PMC(
        storage=tmp_path_factory.mktemp("pmc_storage"),
        figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
    ).get_publications_metadata(ids=ids)
    minimal_number_of_expected_metadata = 350
    assert len(metadata) > minimal_number_of_expected_metadata


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
    publication_metadata = PMC(
        storage=tmp_path_factory.mktemp("pmc_storage"),
        figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
    ).get_publications_metadata(ids=publication_ids)[1]
    assert publication_metadata.year == test_data["publication_date"]
    assert publication_metadata.title == test_data["title"]
    assert publication_metadata.authors == test_data["authors"]
    assert publication_metadata.pmcid == PMCID(test_data["pmcid"])
    assert publication_metadata.pmid == PMID(test_data["pmid"])
    assert publication_metadata.doi == DOI(test_data["doi"])
