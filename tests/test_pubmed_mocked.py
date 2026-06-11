# ruff: noqa: ANN001
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


def test_can_create(mock_entrez, tmp_path_factory: pytest.TempPathFactory):
    """Can create PubMed instance."""
    mock_entrez.responses[mock_entrez.handles["search"]] = {"Count": "5", "IdList": ["1", "2", "3", "4", "5"]}
    actual = PubMed(storage=tmp_path_factory.mktemp("pubmed"), query=Query(search_term="hepg2 thioacetamide"))
    assert actual is not None


def test_get_abstract_not_empty(mock_entrez, tmp_path_factory: pytest.TempPathFactory):
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

    actual = PubMed(
        storage=tmp_path_factory.mktemp("pubmed"),
        query=Query(search_term="hepg2 thioacetamide"),
    ).get_abstracts(ids=[ID("12345"), ID("67890")])
    assert actual is not None
    assert len(actual) > 0


def test_get_id_list(mock_entrez, tmp_path_factory: pytest.TempPathFactory):
    """Get publication count returns correct number."""
    expected = ["36835489", "37913737", "37891562", "36838959"]
    mock_entrez.responses[mock_entrez.handles["search"]] = {"Count": "4", "IdList": expected}

    pubmed_instance = PubMed(
        storage=tmp_path_factory.mktemp("pubmed"),
        query=Query(search_term='(hepg2 methotrexate) AND (("2023"[Date - Entry] : "2023"[Date - Entry]))'),
    )
    actual = pubmed_instance.get_ids()
    number_of_expected_ids = 4
    assert len(actual) == number_of_expected_ids
    assert ID("36835489") in actual
