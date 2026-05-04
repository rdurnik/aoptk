# ruff: noqa: ANN001
from datetime import UTC
from datetime import datetime
import pytest
from aoptk.literature.databases.pubmed import PubMed
from aoptk.literature.databases.pubmed import QueryTooLargeError


@pytest.fixture
def mock_entrez(mocker):
    """Mock Entrez module."""
    return mocker.patch("aoptk.literature.databases.pubmed.Entrez")


def test_can_create(mock_entrez):
    """Can create PubMed instance."""
    mock_entrez.read.return_value = {"Count": "5", "IdList": ["1", "2", "3", "4", "5"]}
    actual = PubMed("hepg2 thioacetamide")
    assert actual is not None


def test_get_abstract_not_empty(mock_entrez):
    """Get abstracts returns non-empty list."""
    mock_entrez.read.side_effect = [
        {"Count": "2", "IdList": ["12345", "67890"]},
        {"Count": "2"},
        {"Count": "2"},
        {
            "PubmedArticle": [
                {
                    "MedlineCitation": {
                        "PMID": "12345",
                        "Article": {
                            "Abstract": {
                                "AbstractText": ["Test abstract text"],
                            },
                        },
                    },
                },
                {
                    "MedlineCitation": {
                        "PMID": "67890",
                        "Article": {
                            "Abstract": {
                                "AbstractText": ["Second abstract"],
                            },
                        },
                    },
                },
            ],
        },
    ]

    actual = PubMed("hepg2 thioacetamide").get_abstracts()
    assert actual is not None
    assert len(actual) > 0


def test_get_publication_count(mock_entrez):
    """Get publication count returns correct number."""
    mock_entrez.read.side_effect = [
        {"Count": "4", "IdList": ["36835489", "37913737", "37891562", "36838959"]},
        {"Count": "4"},
        {"Count": "4"},
    ]

    pubmed_instance = PubMed('(hepg2 methotrexate) AND (("2023"[Date - Entry] : "2023"[Date - Entry]))')
    actual = pubmed_instance.publication_count
    expected = 4
    assert actual == expected


def test_raises_query_too_large_error(mock_entrez):
    """QueryTooLargeError is raised when result count >= maximum_results."""
    mock_entrez.read.side_effect = [
        {"Count": str(PubMed.maximum_results), "IdList": []},
        {"Count": str(PubMed.maximum_results)},
        {"Count": str(PubMed.maximum_results)},
    ]

    with pytest.raises(QueryTooLargeError) as exc_info:
        PubMed("cancer")
    assert exc_info.value.count >= PubMed.maximum_results
    assert exc_info.value.maximum == PubMed.maximum_results


def test_get_id_list(mock_entrez):
    """Get publication count returns correct number."""
    expected = ["36835489", "37913737", "37891562", "36838959"]
    mock_entrez.read.side_effect = [
        {"Count": "4", "IdList": expected},
        {"Count": "4"},
        {"Count": "4"},
    ]

    pubmed_instance = PubMed('(hepg2 methotrexate) AND (("2023"[Date - Entry] : "2023"[Date - Entry]))')
    actual = pubmed_instance.id_list
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
def test_generate_abstracts_for_given_query(
    mock_entrez,
    query: str,
    expected_abstract: str,
    expected_id: str,
    position: int,
):
    """Generate list of abstracts for given query."""
    articles = []
    for i in range(position + 1):
        if i == position:
            articles.append(
                {
                    "MedlineCitation": {
                        "PMID": expected_id,
                        "Article": {
                            "Abstract": {
                                "AbstractText": [expected_abstract] if expected_abstract else [],
                            },
                        },
                    },
                },
            )
        else:
            articles.append(
                {
                    "MedlineCitation": {
                        "PMID": f"dummy_{i}",
                        "Article": {
                            "Abstract": {
                                "AbstractText": [f"Dummy abstract {i}"],
                            },
                        },
                    },
                },
            )

    id_list = [article["MedlineCitation"]["PMID"] for article in articles]

    mock_entrez.read.side_effect = [
        {"Count": str(len(id_list)), "IdList": id_list},
        {"Count": str(len(id_list))},
        {"Count": str(len(id_list))},
        {"PubmedArticle": articles},
    ]

    pubmed_instance = PubMed(query)
    abstracts = pubmed_instance.get_abstracts()
    assert abstracts[position].text == expected_abstract
    assert abstracts[position].id == expected_id


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
def test_get_publication_metadata(mock_entrez, test_data: dict):
    """Generate publication metadata for given id."""
    mock_entrez.read.side_effect = [
        {"Count": "1", "IdList": [test_data["publication_id"]]},
        {"Count": "1"},
        {"Count": "1"},
        [
            {
                "PubDate": f"{test_data['publication_date']}",
                "Title": test_data["title"],
                "AuthorList": test_data["authors"].split(", "),
            },
        ],
    ]

    publication_metadata = PubMed(test_data["publication_id"]).get_publications_metadata()[0]
    assert publication_metadata.id == test_data["publication_id"]
    assert publication_metadata.publication_date == test_data["publication_date"]
    assert publication_metadata.title == test_data["title"]
    assert publication_metadata.authors == test_data["authors"]
    assert publication_metadata.database == test_data["database"]
    assert publication_metadata.search_date.year == datetime.now(UTC).year
    assert publication_metadata.search_date.month == datetime.now(UTC).month
