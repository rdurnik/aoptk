import pandas as pd
import pytest
from aoptk.normalize_chemical import NormalizeChemical
from aoptk.pubchem_synonyms import PubChemSynonyms


def test_can_create():
    actual = PubChemSynonyms(None)
    assert actual is not None

def test_implements_interface():
    assert issubclass(PubChemSynonyms, NormalizeChemical)

def test_normalize_chemical_not_empty():
    actual = PubChemSynonyms(pd.DataFrame()).normalize_chemical("")
    assert actual is not None

@pytest.fixture
def synonyms()->pd.DataFrame:
  content = {"heading": ["acetaminophen", "thioacetamide"], "synonyms": [["paracetamol", "acamol"], ["thiacetamid", "thioacetamid"]]}
  return pd.DataFrame(content)

@pytest.mark.parametrize(("chemical", "expected"), [
    ("acetaminophen", "acetaminophen"),
    ("paracetamol", "acetaminophen"),
    ("thioacetamide", "thioacetamide"),
    ("something_not_in_the_database_but_recognized_as_chemical",
     "something_not_in_the_database_but_recognized_as_chemical"),
])
def test_normalize_chemical_multiple_chemicals(chemical, expected, synonyms):
    assert PubChemSynonyms(synonyms).normalize_chemical(chemical) == expected




