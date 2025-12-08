import pytest
from aoptk.get_abstract import GetAbstract
from aoptk.pubmed import PubMed
from aoptk.pubmed import QueryTooLargeError
import os
from Bio import Entrez

api_key = os.getenv('NCBI_API_KEY')
Entrez.api_key = api_key


def test_can_create():
    """Can create PubMed instance."""
    actual = PubMed("hepg2 thioacetamide")
    assert actual is not None


def test_implements_interface():
    """PubMed implements GetAbstract interface."""
    assert issubclass(PubMed, GetAbstract)


def test_get_abstract_not_empty():
    """Get abstracts returns non-empty list."""
    actual = PubMed("hepg2 thioacetamide").get_abstracts()
    assert actual is not None


def test_get_publication_count():
    """Get publication count returns correct number."""
    actual = PubMed('(hepg2 methotrexate) AND (("2023"[Date - Entry] : "2023"[Date - Entry]))').get_publication_count()
    expected = 4
    assert actual == expected


def test_too_many_results():
    """Raises SystemExit for too many results."""
    with pytest.raises(QueryTooLargeError):
        PubMed("cancer").get_abstracts()


@pytest.mark.parametrize(
    ("query", "expected_abstract", "expected_id"),
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
        ),
    ],
)
def test_generate_abstracts_for_given_query(query: str, expected_abstract: str, expected_id: str):
    """Generate list of abstracts for given query."""
    abstract = PubMed(query).get_abstracts()[3].text
    publication_id = PubMed(query).get_abstracts()[3].publication_id
    assert abstract == expected_abstract
    assert publication_id == expected_id
