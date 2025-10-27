from aoptk.normalize_chemical import NormalizeChemical
from aoptk.mesh_terms import MeshTerms
import pandas as pd
import pytest

def test_can_create():
    actual = MeshTerms(None)
    assert actual is not None

def test_implements_interface():
    assert issubclass(MeshTerms, NormalizeChemical)

def test_normalize_chemical_not_empty():
    actual = MeshTerms(pd.DataFrame()).normalize_chemical('')
    assert actual is not None

# Probably should have written some tests here for the database?

@pytest.fixture
def mesh_terms()->pd.DataFrame:
  content = {'heading': ['acetaminophen', 'thioacetamide'], 'mesh_terms': [['paracetamol', 'acamol'], ['thiacetamid', 'thioacetamid']]}
  df = pd.DataFrame(content)
  return df

# For purposes of testing, we need to have a smaller database of PubChem, otherwise the test will take too long.
@pytest.mark.parametrize(("chemical", "expected"), [
    ("acetaminophen", "acetaminophen"),
    ("paracetamol", "acetaminophen"),
    ("thioacetamide", "thioacetamide"),
    ("something_not_in_the_database_but_recognized_as_chemical",
     "something_not_in_the_database_but_recognized_as_chemical"),
])
def test_normalize_chemical_multiple_chemicals(chemical, expected, mesh_terms):
    assert MeshTerms(mesh_terms).normalize_chemical(chemical) == expected





    



