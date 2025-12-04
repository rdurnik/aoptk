import pytest
from aoptk.europepmc import EuropePMC
from aoptk.get_abstract import GetAbstract


def test_can_create():
    """Can create EuropePMC instance."""
    actual = EuropePMC("")
    assert actual is not None


def test_implements_interface():
    """EuropePMC implements GetAbstract interface."""
    assert issubclass(EuropePMC, GetAbstract)


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
    assert publication_id == expected_id


@pytest.mark.parametrize(
    ("query", "expected_abstract", "expected_id"),
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
        ),
    ],
)
def test_generate_abstracts_for_given_query(query: str, expected_abstract: str, expected_id: str):
    """Generate list of abstracts for given query."""
    abstract = EuropePMC(query).get_abstracts()[0].text
    publication_id = EuropePMC(query).get_abstracts()[0].publication_id
    assert abstract == expected_abstract
    assert publication_id == expected_id
