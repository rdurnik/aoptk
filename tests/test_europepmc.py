from __future__ import annotations
import shutil
from datetime import datetime
from datetime import timezone
from pathlib import Path
import pytest
from requests import HTTPError
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.literature.id import ID


def test_can_create():
    """Test that EuropePMCPDF can be instantiated."""
    actual = EuropePMC("")
    assert actual is not None


def test_get_publication_data_not_empty():
    """Test that pdfs() method returns non-empty list."""
    actual = EuropePMC("").pdfs()
    assert actual is not None


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        (
            "liver fibrosis AND thioacetamide AND mg/kg AND weeks AND Ayurveda AND (FIRST_PDATE:[2023 TO 2024])",
            ["39705085", "PMC11420034", "PMC9962064", "PMC11059288", "PMC10829571"],
        ),
    ],
)
def test_return_id_list(query: str, expected: list[str]):
    """Test that get_id() returns expected publication IDs."""
    actual = EuropePMC(query).get_id()
    assert actual == expected


@pytest.mark.parametrize(
    ("query", "expected", "query_for_abstracts_only", "remove_reviews"),
    [
        (
            "spheroid methotrexate thioacetamide AND (FIRST_PDATE:[2021 TO 2023])",
            [
                "PMC10647544",
                "PMC9857994",
                "PMC8950395",
                "PMC8201787",
                "PMC9256002",
                "PMC7911320",
                "PMC10928813",
                "PMC10576948",
                "PMC8934723",
                "PMC9243943",
            ],
            False,
            False,
        ),
        (
            "spheroid methotrexate AND (FIRST_PDATE:[2020 TO 2021])",
            ["PMC8230402", "PMC7348038", "PMC8638776", "PPR380866", "PMC8649206", "PMC8476350", "PPR190639"],
            True,
            False,
        ),
        (
            "spheroid methotrexate hepg2 AND (FIRST_PDATE:[2024 TO 2024])",
            [
                "PMC11201042",
                "PMC11354664",
                "PMC11156946",
                "PMC12149029",
                "PMC11208286",
                "PMC11245638",
                "PMC11177578",
                "PMC11470995",
            ],
            False,
            True,
        ),
        (
            "spheroid methotrexate AND (FIRST_PDATE:[2020 TO 2024])",
            [
                "PMC11354664",
                "PPR875796",
                "39060210",
                "37454032",
                "PMC9358508",
                "PMC9434104",
                "PMC8230402",
                "PMC7348038",
                "PMC8638776",
                "PPR380866",
                "PMC8649206",
                "PMC8476350",
                "PPR190639",
            ],
            True,
            True,
        ),
    ],
)
def test_ids_not_to_return(query: str, expected: list[str], query_for_abstracts_only: bool, remove_reviews: bool):
    """Test that get_id_list() returns expected publication IDs with query modifications."""
    sut = EuropePMC(query)
    if query_for_abstracts_only:
        sut = sut.abstracts_only()
    if remove_reviews:
        sut = sut.remove_reviews()
    actual = sut.get_id()
    assert actual == expected


def test_open_access_europepmc_pdf_file_exists():
    """Test that an open access EuropePMC PDF can be retrieved and saved."""
    EuropePMC("PMC8614944").pdfs()
    filepath = Path("tests/pdf_storage") / "PMC8614944.pdf"
    assert filepath.exists()
    assert filepath.is_file()
    assert filepath.stat().st_size > 0
    shutil.rmtree("tests/pdf_storage", ignore_errors=True)


@pytest.mark.parametrize("pubmed_id", ["41107038", "26733159"])
@pytest.mark.xfail(raises=HTTPError)
def test_metapub_pdf_file_exists(pubmed_id: str):
    """Test that a PDF retrieved via PubMed can be saved."""
    storage = Path("tests/pdf_storage")
    sut = EuropePMC(pubmed_id, storage=storage)
    sut.pdfs()
    filepath = storage / f"{pubmed_id}.pdf"
    assert filepath.exists()
    assert filepath.is_file()
    assert filepath.stat().st_size > 0
    shutil.rmtree(storage, ignore_errors=True)


def test_get_abstract_not_empty():
    """Get abstracts returns non-empty list."""
    actual = EuropePMC("").get_abstracts()
    assert actual is not None


@pytest.mark.parametrize(
    ("publication_id", "expected_abstract", "expected_id"),
    [
        (
            "30784932",
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
        ),
        (
            "PMC12533043",
            "How developing organisms respond to a changing environment is a fundamental question. "
            "Pollutants and temperature are major environmental factors. Using the bristle patterning"
            " of Drosophila as a model system, we observed that cold temperature and methotrexate, "
            "a medical drug that contaminates wastewaters, increase dorsocentral (DC) bristle number, "
            "a trait normally robust. The patterning of bristles is well understood and involves the "
            "achaete-scute (ac-sc) proneural genes. Modular enhancers activate ac-sc expression in "
            "groups of cells, called proneural clusters, from which bristle precursors are selected"
            " by lateral inhibition, a process involving Notch signalling and ac-sc auto-activation."
            " In addition, ac-sc basal expression is controlled by a cocktail of repressive factors. "
            "We observed that the deletion of the DC enhancer prevents the induction of ectopic DC "
            "bristles by methotrexate but does not stop low temperature to induce DC bristles."
            " Indeed, we show that methotrexate has a strong synergy with mutants of factors that "
            "regulate the DC enhancer and extends the zone of activity of this enhancer. In contrast, "
            "temperature interacts with repressors of ac-sc basal expression. Thus, methotrexate and"
            " temperature both affect DC bristle patterning but by distinct mechanisms, methotrexate "
            "on the DC enhancer and cold independently of this enhancer.",
            "PMC12533043",
        ),
    ],
)
def test_generate_abstract_for_given_id(publication_id: str, expected_abstract: str, expected_id: str):
    """Generate abstract for given query."""
    abstract = EuropePMC("").get_abstract(publication_id).text
    publication_id = EuropePMC("").get_abstract(publication_id).publication_id
    assert abstract == expected_abstract
    assert publication_id == ID(expected_id)


@pytest.mark.parametrize(
    ("query", "expected_abstract", "expected_id", "position"),
    [
        (
            "TITLE_ABS:(liver cancer AND hepg2 AND thioacetamide) AND (FIRST_PDATE:[2018 TO 2019])",
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
            "PMC5594291 OR PMC5596756",
            "",
            "PMC5596756",
            1,
        ),
    ],
)
@pytest.mark.xfail(raises=HTTPError)
def test_generate_abstracts_for_given_query(query: str, expected_abstract: str, expected_id: str, position: int):
    """Generate list of abstracts for given query."""
    abstract = EuropePMC(query).get_abstracts()[position].text
    publication_id = EuropePMC(query).get_abstracts()[position].publication_id
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
def test_get_publication_metadata(test_data: dict):
    """Generate publication metadata for given id."""
    publication_metadata = EuropePMC(test_data["publication_id"]).get_publications_metadata()[0]
    assert publication_metadata.publication_id == test_data["publication_id"]
    assert publication_metadata.publication_date == test_data["publication_date"]
    assert publication_metadata.title == test_data["title"]
    assert publication_metadata.authors == test_data["authors"]
    assert publication_metadata.database == test_data["database"]
    assert publication_metadata.search_date.year == datetime.now(timezone.utc).year
    assert publication_metadata.search_date.month == datetime.now(timezone.utc).month
