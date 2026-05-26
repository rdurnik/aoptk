import json
from http.client import RemoteDisconnected
from pathlib import Path
from urllib.error import HTTPError
import pytest
from fuzzywuzzy import fuzz
from aoptk.literature.databases.pubmed import PubMed
from aoptk.literature.get_abstract import GetAbstract
from aoptk.literature.get_id import GetID
from aoptk.literature.get_publication_metadata import GetPublicationMetadata
from aoptk.literature.id import DOI
from aoptk.literature.id import ID
from aoptk.literature.id import PMCID
from aoptk.literature.id import PMID
from aoptk.literature.query import Query

# ruff: noqa: PLR2004

metadata_test = json.loads(Path("tests/test-data/ncbi_metadata.json").read_text(encoding="utf-8"))


@pytest.mark.xfail(raises=HTTPError)
def test_can_create():
    """Can create PubMed instance."""
    actual = PubMed()
    assert actual is not None


def test_implements_interface():
    """PubMed implements GetAbstract interface."""
    assert issubclass(PubMed, GetAbstract)
    assert issubclass(PubMed, GetID)
    assert issubclass(PubMed, GetPublicationMetadata)


@pytest.mark.xfail(raises=HTTPError)
def test_get_abstract_not_empty():
    """Get abstracts returns non-empty list."""
    actual = PubMed().get_abstracts(ids=[])
    assert actual is not None


@pytest.mark.xfail(raises=HTTPError)
def test_get_id():
    """Test that get_id returns correct IDs."""
    actual = PubMed(
        query=Query(search_term='(hepg2 methotrexate) AND (("2023"[Date - Entry] : "2023"[Date - Entry]))'),
    ).get_ids()
    number_of_expected_ids = 4
    assert len(actual) == number_of_expected_ids
    assert ID("36835489") in actual


@pytest.mark.parametrize(
    ("ids", "expected_abstract"),
    [
        (
            [ID("36835489"), ID("40785269")],
            Path("tests/test-data/PMC12416454_abstract.txt").read_text(encoding="utf-8"),
        ),
        (
            [ID("30493944"), ID("29140036")],
            "",
        ),
    ],
)
@pytest.mark.xfail(raises=HTTPError)
def test_generate_abstracts_for_given_query(ids: list[ID], expected_abstract: str):
    """Generate list of abstracts for given query."""
    abstract = PubMed().get_abstracts(ids=ids)[1]
    ratio = fuzz.ratio(abstract.text, expected_abstract)
    assert ratio >= 75


@pytest.mark.parametrize(
    ("publication_ids", "test_data"),
    [
        ([ID("34028753"), ID("41345959")], metadata_test[0]),
        ([ID("34028753"), ID("40785269")], metadata_test[1]),
    ],
)
@pytest.mark.xfail(raises=HTTPError)
def test_get_publication_metadata(publication_ids: list[ID], test_data: dict):
    """Generate publication metadata for given id."""
    publication_metadata = PubMed().get_publications_metadata(ids=publication_ids)[1]
    assert publication_metadata.year == test_data["publication_date"]
    assert publication_metadata.title == test_data["title"]
    assert publication_metadata.authors == test_data["authors"]
    assert publication_metadata.id == publication_ids[1]
    assert publication_metadata.pmcid == PMCID(test_data["pmcid"])
    assert publication_metadata.pmid == PMID(test_data["pmid"])
    assert publication_metadata.doi == DOI(test_data["doi"])


@pytest.mark.parametrize(
    ("query", "ids_to_return", "ids_not_to_return"),
    [
        (
            Query(
                search_term=("liver fibrosis"),
                date=("2023", "01", "30"),
            ),
            ["36717776", "36739734", "36864944"],
            ["32260126", "32389810", "32061651"],
        ),
        (
            Query(
                search_term=("liver fibrosis thioacetamide"),
                full_text_subset=True,
            ),
            ["34028753", "30288660", "40187163"],
            ["31592593", "6577229", "37599493"],
        ),
        (
            Query(search_term=("cancer"), full_text_subset=True, date=("2024", "04", "02")),
            ["38563834", "38566201", "38156967"],
            ["38564116"],
        ),
        (
            Query(
                search_term=("methotrexate thioacetamide"),
                exclude_preprint=True,
            ),
            ["25829334", "39637935", "8841488"],
            [],
        ),
    ],
)
@pytest.mark.xfail(raises=HTTPError)
def test_query_filtering(
    query: Query,
    ids_to_return: list[str],
    ids_not_to_return: list[str],
):
    """Test that the query filters results correctly."""
    sut = PubMed(
        query=query,
    )
    actual_ids = sut.get_ids()
    for publication_id in ids_to_return:
        assert publication_id in actual_ids
    for publication_id in ids_not_to_return:
        assert publication_id not in actual_ids


@pytest.mark.xfail(raises=HTTPError)
def test_preprint_filtering():
    """Test that the preprint filter works correctly."""
    sut = PubMed(
        query=Query(
            search_term="liver cancer",
            only_preprint=True,
        ),
    )
    actual_ids = sut.get_ids()
    approx_number_of_preprints = 10000
    assert len(actual_ids) < approx_number_of_preprints


@pytest.mark.xfail(raises=HTTPError)
def test_exclude_only_preprint():
    """Test that the preprint filter works correctly."""
    sut = PubMed(
        query=Query(
            search_term="liver cancer",
            only_preprint=True,
            exclude_preprint=True,
        ),
    )
    actual_ids = sut.get_ids()
    assert len(actual_ids) == 0


@pytest.mark.xfail(raises=(HTTPError, RemoteDisconnected))
def test_get_id_large_query():
    """Test that get_id() method returns a list of publication IDs."""
    actual = len(
        PubMed(
            query=Query(
                search_term="fibrosis 2019/01/15:2019/07/30[dp]",
            ),
        ).get_ids(),
    )
    expected = 10117
    assert actual == pytest.approx(expected, abs=100)


def test_generate_abstracts_multiple_abstracts():
    """Generate list of abstracts for given query."""
    ids = PubMed(
        query=Query(search_term="thioacetamide liver fibrosis cancer"),
    ).get_ids()
    abstracts = PubMed().get_abstracts(ids=ids)
    minimal_number_of_expected_abstracts = 150
    assert len(abstracts) > minimal_number_of_expected_abstracts


def test_generate_metadata_multiple_publications():
    """Generate list of publication metadata for given query."""
    ids = PubMed(
        query=Query(search_term="thioacetamide liver fibrosis"),
    ).get_ids()
    metadata = PubMed().get_publications_metadata(ids=ids)
    minimal_number_of_expected_metadata = 1100
    assert len(metadata) > minimal_number_of_expected_metadata
