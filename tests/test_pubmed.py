from datetime import datetime
from datetime import timezone
from urllib.error import HTTPError
import pytest
from aoptk.literature.databases.pubmed import PubMed
from aoptk.literature.databases.pubmed import QueryTooLargeError
from aoptk.literature.get_abstract import GetAbstract


@pytest.mark.xfail(raises=HTTPError)
def test_can_create():
    """Can create PubMed instance."""
    actual = PubMed("hepg2 thioacetamide")
    assert actual is not None


def test_implements_interface():
    """PubMed implements GetAbstract interface."""
    assert issubclass(PubMed, GetAbstract)


@pytest.mark.xfail(raises=HTTPError)
def test_get_abstract_not_empty():
    """Get abstracts returns non-empty list."""
    actual = PubMed("hepg2 thioacetamide").get_abstracts()
    assert actual is not None


@pytest.mark.xfail(raises=HTTPError)
def test_get_publication_count():
    """Get publication count returns correct number."""
    actual = PubMed('(hepg2 methotrexate) AND (("2023"[Date - Entry] : "2023"[Date - Entry]))').get_publication_count()
    expected = 4
    assert actual == expected


@pytest.mark.xfail(raises=HTTPError)
def test_raises_query_too_large_error():
    """QueryTooLargeError is raised  when result count >= maximum_results."""
    with pytest.raises(QueryTooLargeError) as exc_info:
        PubMed("cancer")
    assert exc_info.value.count >= PubMed.maximum_results
    assert exc_info.value.maximum == PubMed.maximum_results


@pytest.mark.xfail(raises=HTTPError)
def test_get_id():
    """Test that get_id returns correct IDs."""
    actual = PubMed('(hepg2 methotrexate) AND (("2023"[Date - Entry] : "2023"[Date - Entry]))').get_id()
    expected = ["36835489", "37913737", "37891562", "36838959"]
    assert sorted(actual) == sorted(expected)


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
    abstract = PubMed(query).get_abstracts()[position].text
    publication_id = PubMed(query).get_abstracts()[position].publication_id
    assert abstract == expected_abstract
    assert publication_id == expected_id


@pytest.mark.parametrize(
    "test_data",
    [
        {
            "publication_id": "41345959",
            "publication_date": "2025",
            "title": "YAP-induced MAML1 cooperates with STAT3 to drive hepatocellular carcinoma progression.",
            "authors": "Li J, Li X, Wang R, Li M, Xiao Y",
            "database": "PubMed",
        },
        {
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
    publication_metadata = PubMed(test_data["publication_id"]).get_publications_metadata()[0]
    assert publication_metadata.publication_id == test_data["publication_id"]
    assert publication_metadata.publication_date == test_data["publication_date"]
    assert publication_metadata.title == test_data["title"]
    assert publication_metadata.authors == test_data["authors"]
    assert publication_metadata.database == test_data["database"]
    assert publication_metadata.search_date.year == datetime.now(timezone.utc).year
    assert publication_metadata.search_date.month == datetime.now(timezone.utc).month
