from datetime import UTC
from datetime import datetime
from http.client import RemoteDisconnected
from urllib.error import HTTPError
import pytest
from aoptk.literature.databases.pubmed import PubMed
from aoptk.literature.get_abstract import GetAbstract
from aoptk.literature.get_id import GetID
from aoptk.literature.get_publication_metadata import GetPublicationMetadata
from aoptk.literature.id import ID
from aoptk.literature.query import Query


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
    ("query", "expected_abstract", "expected_id", "position"),
    [
        (
            '(hepg2 methotrexate) AND (("2023"[Date - Entry] : "2023"[Date - Entry]))',
            "Copper carbosilane metallodendrimers containing chloride ligands and nitrate ligands"
            " were mixed with commercially available conventional anticancer drugs, doxorubicin,"
            " methotrexate and 5-fluorouracil, for a possible therapeutic system. To verify the"
            " hypothesis that copper metallodendrimers can form conjugates with anticancer drugs,"
            " their complexes were biophysically characterized using zeta potential and zeta size"
            " methods. Next, to confirm the existence of a synergetic effect of dendrimers and"
            " drugs, in vitro studies were performed. The combination therapy has been applied"
            " in two cancer cell lines: MCF-7 (human breast cancer cell line) and HepG2 (human"
            " liver carcinoma cell line). The doxorubicin (DOX), methotrexate (MTX) and 5-fluorouracil"
            " (5-FU) were more effective against cancer cells when conjugated with copper "
            "metallodendrimers. Such combination significantly decreased cancer cell"
            " viability when compared to noncomplexed drugs or dendrimers. The"
            " incubation of cells with drug/dendrimer complexes resulted in the"
            " increase of the reactive oxygen species (ROS) levels and the depolarization "
            "of mitochondrial membranes. Copper ions present in the dendrimer structures "
            "enhanced the anticancer properties of the whole nanosystem and improved drug "
            "effects, inducing both the apoptosis and necrosis of MCF-7 (human breast cancer "
            "cell line) and HepG2 (human liver carcinoma cell line) cancer cells.",
            "36835489",
            3,
        ),
        (
            "30493944, 29140036",
            "",
            "29140036",
            1,
        ),
    ],
)
@pytest.mark.xfail(raises=HTTPError)
def test_generate_abstracts_for_given_query(query: str, expected_abstract: str, expected_id: str, position: int):
    """Generate list of abstracts for given query."""
    ids = PubMed(query=Query(search_term=query)).get_ids()
    abstract = PubMed().get_abstracts(ids=ids)[position].text
    publication_id = PubMed().get_abstracts(ids=ids)[position].id
    assert abstract == expected_abstract
    assert publication_id == expected_id


# TEST THE SECOND PUBLICATION INSTEAD, INPUT A LIST
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "publication_ids": [ID("34028753"), ID("41345959")],
            "publication_id": "41345959",
            "publication_date": "2025",
            "title": "YAP-induced MAML1 cooperates with STAT3 to drive hepatocellular carcinoma progression.",
            "authors": "Li J, Li X, Wang R, Li M, Xiao Y",
            "database": "PubMed",
        },
        {
            "publication_ids": [ID("34028753"), ID("40785269")],
            "publication_id": "40785269",
            "publication_date": "2025",
            "title": "Flexibility-Aided Orientational Self-Sorting and "
            "Transformations of Bioactive Homochiral Cuboctahedron Pd(12)L(16).",
            "authors": "Chattopadhyay S, Durník R, Kiesilä A, Kalenius E, Linnanto JM, "
            "Babica P, Kuta J, Marek R, Jurček O",
            "database": "PubMed",
        },
    ],
)
@pytest.mark.xfail(raises=HTTPError)
def test_get_publication_metadata(test_data: dict):
    """Generate publication metadata for given id."""
    publication_metadata = PubMed().get_publications_metadata(ids=test_data["publication_ids"])[1]
    assert publication_metadata.id == test_data["publication_id"]
    assert publication_metadata.publication_date == test_data["publication_date"]
    assert publication_metadata.title == test_data["title"]
    assert publication_metadata.authors == test_data["authors"]
    assert publication_metadata.database == test_data["database"]
    assert publication_metadata.search_date.year == datetime.now(UTC).year
    assert publication_metadata.search_date.month == datetime.now(UTC).month


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
