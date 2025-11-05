from aoptk.get_publication import GetPublication
from aoptk.get_europepmc_publication import GetEuropePMCPublication
import pandas as pd
import pytest
import os
import shutil

def test_can_create():
    actual = GetEuropePMCPublication(str)
    assert actual is not None

def test_implements_interface():
    assert issubclass(GetEuropePMCPublication, GetPublication)

def test_get_publication_data_not_empty():
    actual = GetEuropePMCPublication('').get_publication()
    assert actual is not None

@pytest.mark.parametrize(("query", "expected"), [
    ('liver fibrosis AND thioacetamide AND mg/kg AND weeks AND Ayurveda AND (FIRST_PDATE:[2023 TO 2024])', ['39705085', 'PMC11420034', 'PMC9962064', 'PMC11059288', 'PMC10829571']),
])
def test_return_id_list(query, expected):
    actual = GetEuropePMCPublication(query).get_id_list()
    assert actual == expected

@pytest.mark.parametrize(("query", "expected", "query_for_abstracts_only", "remove_reviews"), [
    ('spheroid methotrexate thioacetamide AND (FIRST_PDATE:[2021 TO 2023])', ['PMC10647544', 'PMC9857994', 'PMC8950395', 'PMC8201787', 'PMC9256002', 'PMC7911320', 'PMC10928813', 'PMC10576948', 'PMC8934723', 'PMC9243943'], False, False),
    ('spheroid methotrexate AND (FIRST_PDATE:[2020 TO 2021])', ['PMC8230402', 'PMC7348038', 'PMC8638776', 'PPR380866', 'PMC8649206', 'PMC8476350', 'PPR190639'], True, False),
    ('spheroid methotrexate hepg2 AND (FIRST_PDATE:[2024 TO 2024])', ['PMC11201042', 'PMC11354664', 'PMC11156946', 'PMC11208286', 'PMC11245638', 'PMC11177578', 'PMC11470995'], False, True),
    ('spheroid methotrexate AND (FIRST_PDATE:[2020 TO 2024])', ['PMC11354664', 'PPR875796', '39060210', '37454032', 'PMC9358508', 'PMC9434104', 'PMC8230402', 'PMC7348038', 'PMC8638776', 'PPR380866', 'PMC8649206', 'PMC8476350', 'PPR190639'], True, True),
])
def test_ids_not_to_return(query, expected, query_for_abstracts_only, remove_reviews):
    actual = GetEuropePMCPublication(query).modify_query(query_for_abstracts_only, remove_reviews).get_id_list()
    assert actual == expected

def test_open_access_europepmc_pdf_file_exists():
    actual = GetEuropePMCPublication("PMC8614944").get_publication()
    filepath = os.path.join('tests/pdf_storage', 'PMC8614944.pdf')
    assert os.path.exists(filepath)
    assert os.path.isfile(filepath)
    assert os.path.getsize(filepath) > 0
    shutil.rmtree('tests/pdf_storage', ignore_errors=True)

def test_metapub_pdf_file_exists():
    actual = GetEuropePMCPublication("41107038").get_publication()
    filepath = os.path.join('tests/pdf_storage', '41107038.pdf')
    assert os.path.exists(filepath)
    assert os.path.isfile(filepath)
    assert os.path.getsize(filepath) > 0
    shutil.rmtree('tests/pdf_storage', ignore_errors=True)

def test_generate_abstract_for_given_query():
    actual = GetEuropePMCPublication(str).get_europepmc_json('TITLE_ABS:(liver cancer AND hepg2 AND thioacetamide) AND (FIRST_PDATE:[2018 TO 2019])')
    expected = "Insulin growth factor (IGF) family and their receptors play a great role in tumors' development. In addition, IGF-1 enhances cancer progression through regulating cell proliferation, angiogenesis, immune modulation and metastasis. Moreover, nicotinamide is association with protection against cancer. Therefore, we conducted this research to examine the therapeutic effects of nicotinamide against hepatocellular carcinoma (HCC) both in vivo and in vitro through affecting IGF-1 and the balance between PKB and Nrf2. HCC was induced in rats by 200 mg/kg, ip thioacetamide. The rat survival, number and size of tumors and serum α-fetoprotein (AFP) were measured. The gene and protein levels of IGF-1, Nrf2, PKB and JNK-MAPK were assessed in rat livers. In addition, HepG2 cells, human HCC cell lines, were treated with different concentrations of nicotinamide. We found that nicotinamide enhanced the rats' survival and reduced the number and size of hepatic tumors as well as it reduced serum AFP and HepG2 cells survival. Nicotinamide ameliorated HCC-induced reduction in the expression of Nrf2. Moreover, nicotinamide blocked HCC-induced elevation in IGF-1, PKB and JNK-MAPK. In conclusion, nicotinamide produced cytotoxic effects against HCC both in vivo and in vitro. The cytotoxic activity can be explained by inhibition of HCC-induced increased in the expression of IGF-1 and leads to disturbances in the balance between the cell death signal by PKB and MAPK; and the cell survival signal by Nrf2, directing it towards cell survival signals in normal liver cells providing more protection for body against tumor."
    assert actual == expected

@pytest.mark.parametrize(("id", "expected"), [
    ("123456", False),
    ("PMC123456", True),
])
def test_is_europepmc_id(id, expected):
    actual = GetEuropePMCPublication(str).is_europepmc_id(id)
    assert actual == expected


# Tests for when Europe PMC / PubMed is not available. Tests for internet connection issues.
