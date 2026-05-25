# ruff: noqa: ANN001
from datetime import UTC
from datetime import datetime
import pytest
from aoptk.literature.databases.pubmed import PubMed
from aoptk.literature.id import ID
from aoptk.literature.query import Query


@pytest.fixture
def mock_entrez(mocker):
    """Provide a simple Entrez mock with handle-based `read` returns."""
    ent = mocker.patch("aoptk.literature.databases.pubmed.Entrez")
    mocker.patch("aoptk.literature.databases.ncbi.Entrez", new=ent)

    ent.handles = {
        "search": mocker.MagicMock(name="esearch_handle"),
        "fetch": mocker.MagicMock(name="efetch_handle"),
        "summary": mocker.MagicMock(name="esummary_handle"),
    }

    ent.esearch.return_value = ent.handles["search"]
    ent.efetch.return_value = ent.handles["fetch"]
    ent.esummary.return_value = ent.handles["summary"]
    ent.responses = {}
    ent.read.side_effect = ent.responses.get
    return ent


def test_can_create(mock_entrez):
    """Can create PubMed instance."""
    mock_entrez.responses[mock_entrez.handles["search"]] = {"Count": "5", "IdList": ["1", "2", "3", "4", "5"]}
    actual = PubMed(query=Query(search_term="hepg2 thioacetamide"))
    assert actual is not None


def test_get_abstract_not_empty(mock_entrez):
    """Get abstracts returns non-empty list."""
    mock_entrez.responses[mock_entrez.handles["search"]] = {"Count": "2", "IdList": ["12345", "67890"]}
    mock_entrez.responses[mock_entrez.handles["fetch"]] = {
        "PubmedArticle": [
            {
                "MedlineCitation": {
                    "PMID": "12345",
                    "Article": {"Abstract": {"AbstractText": ["Test abstract text"]}},
                },
            },
            {
                "MedlineCitation": {
                    "PMID": "67890",
                    "Article": {"Abstract": {"AbstractText": ["Second abstract"]}},
                },
            },
        ],
    }

    actual = PubMed(query=Query(search_term="hepg2 thioacetamide")).get_abstracts(ids=[ID("12345"), ID("67890")])
    assert actual is not None
    assert len(actual) > 0


def test_get_id_list(mock_entrez):
    """Get publication count returns correct number."""
    expected = ["36835489", "37913737", "37891562", "36838959"]
    mock_entrez.responses[mock_entrez.handles["search"]] = {"Count": "4", "IdList": expected}

    pubmed_instance = PubMed(
        query=Query(search_term='(hepg2 methotrexate) AND (("2023"[Date - Entry] : "2023"[Date - Entry]))'),
    )
    actual = pubmed_instance.get_ids()
    number_of_expected_ids = 4
    assert len(actual) == number_of_expected_ids
    assert ID("36835489") in actual


@pytest.mark.parametrize(
    "test_data",
    [
        {
            "publication_id": ID("41345959"),
            "publication_date": "2025",
            "title": "YAP-induced MAML1 cooperates with STAT3 to drive hepatocellular carcinoma progression.",
            "authors": "Li J, Li X, Wang R, Li M, Xiao Y",
            "database": "PubMed",
        },
        {
            "publication_id": ID("40785269"),
            "publication_date": "2025",
            "title": "Flexibility-Aided Orientational Self-Sorting and "
            "Transformations of Bioactive Homochiral Cuboctahedron Pd(12)L(16).",
            "authors": "Chattopadhyay S, Durník R, Kiesilä A, Kalenius E, Linnanto JM, "
            "Babica P, Kuta J, Marek R, Jurček O",
            "database": "PubMed",
        },
    ],
)
def test_get_publication_metadata(mock_entrez, test_data: dict):
    """Generate publication metadata for given id."""
    mock_entrez.responses[mock_entrez.handles["search"]] = {"Count": "1", "IdList": [str(test_data["publication_id"])]}
    mock_entrez.responses[mock_entrez.handles["summary"]] = [
        {
            "Id": str(test_data["publication_id"]),
            "PubDate": f"{test_data['publication_date']}",
            "Title": test_data["title"],
            "AuthorList": test_data["authors"].split(", "),
        },
    ]

    publication_metadata = PubMed().get_publications_metadata(ids=[test_data["publication_id"]])[0]
    assert publication_metadata.id == test_data["publication_id"]
    assert publication_metadata.publication_date == test_data["publication_date"]
    assert publication_metadata.title == test_data["title"]
    assert publication_metadata.authors == test_data["authors"]
    assert publication_metadata.database == test_data["database"]
    assert publication_metadata.search_date.year == datetime.now(UTC).year
    assert publication_metadata.search_date.month == datetime.now(UTC).month
