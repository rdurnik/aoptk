import os
import shutil
import pytest
from aoptk.europepmc import EuropePMC
from aoptk.get_pdf import GetPDF


def test_can_create():
    actual = EuropePMC("")
    assert actual is not None

def test_implements_interface():
    assert issubclass(EuropePMC, GetPDF)

def test_get_publication_data_not_empty():
    actual = EuropePMC("").pdfs()
    assert actual is not None

@pytest.mark.parametrize(("query", "expected"), [
    ("liver fibrosis AND thioacetamide AND mg/kg AND weeks AND Ayurveda AND (FIRST_PDATE:[2023 TO 2024])", ["39705085", "PMC11420034", "PMC9962064", "PMC11059288", "PMC10829571"]),
])
def test_return_id_list(query, expected):
    actual = EuropePMC(query).get_id_list()
    assert actual == expected

@pytest.mark.parametrize(("query", "expected", "query_for_abstracts_only", "remove_reviews"), [
    ("spheroid methotrexate thioacetamide AND (FIRST_PDATE:[2021 TO 2023])", ["PMC10647544", "PMC9857994", "PMC8950395", "PMC8201787", "PMC9256002", "PMC7911320", "PMC10928813", "PMC10576948", "PMC8934723", "PMC9243943"], False, False),
    ("spheroid methotrexate AND (FIRST_PDATE:[2020 TO 2021])", ["PMC8230402", "PMC7348038", "PMC8638776", "PPR380866", "PMC8649206", "PMC8476350", "PPR190639"], True, False),
    ("spheroid methotrexate hepg2 AND (FIRST_PDATE:[2024 TO 2024])", ["PMC11201042", "PMC11354664", "PMC11156946", "PMC11208286", "PMC11245638", "PMC11177578", "PMC11470995"], False, True),
    ("spheroid methotrexate AND (FIRST_PDATE:[2020 TO 2024])", ["PMC11354664", "PPR875796", "39060210", "37454032", "PMC9358508", "PMC9434104", "PMC8230402", "PMC7348038", "PMC8638776", "PPR380866", "PMC8649206", "PMC8476350", "PPR190639"], True, True),
])
def test_ids_not_to_return(query, expected, query_for_abstracts_only, remove_reviews):
    sut = EuropePMC(query)
    if query_for_abstracts_only:
        sut = sut.abstracts_only()
    if remove_reviews:
        sut = sut.remove_reviews()
    actual = sut.get_id_list()
    assert actual == expected

def test_open_access_europepmc_pdf_file_exists():
    actual = EuropePMC("PMC8614944").pdfs()
    filepath = os.path.join("tests/pdf_storage", "PMC8614944.pdf")
    assert os.path.exists(filepath)
    assert os.path.isfile(filepath)
    assert os.path.getsize(filepath) > 0
    shutil.rmtree("tests/pdf_storage", ignore_errors=True)

def test_metapub_pdf_file_exists():
    actual = EuropePMC("41107038").pdfs()
    filepath = os.path.join("tests/pdf_storage", "41107038.pdf")
    assert os.path.exists(filepath)
    assert os.path.isfile(filepath)
    assert os.path.getsize(filepath) > 0
    shutil.rmtree("tests/pdf_storage", ignore_errors=True)



# Tests for when Europe PMC / PubMed is not available. Tests for internet connection issues.
