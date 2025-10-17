from aoptk.normalize_chemical import NormalizeChemical
from aoptk.mesh_terms import MeshTerms
import pandas as pd
import pytest

def test_can_create():
    actual = MeshTerms()
    assert actual is not None

def test_implements_interface():
    assert issubclass(MeshTerms, NormalizeChemical)

def test_normalize_chemical_not_empty():
    actual = MeshTerms().normalize_chemical('')
    assert actual is not None

# I made this work with simply returnign acetaminophen...
def test_normalize_chemical_acetaminophen():
    actual = MeshTerms().normalize_chemical(chemical='acetaminophen')
    assert actual == 'acetaminophen'

# But I knew it will not work for all chemicals... I need a database of MeSH terms
def test_get_database_for_normalization_not_empty():
    actual = MeshTerms().get_database_for_normalization()
    assert actual is not None

# Probably should have written some tests here for the database?

# Then I did tests for many chemicals
@pytest.mark.parametrize(("chemical", "expected"), [
    ("acetaminophen", "acetaminophen"),
    ("acamol", "acetaminophen"),
    ("thioacetamide", "thioacetamide"),
    ("something_not_in_the_database_but_recognized_as_chemical",
     "something_not_in_the_database_but_recognized_as_chemical"),
     ("CH3OH", "CH3OH")
])
def test_normalize_chemical_multiple_chemicals(chemical, expected):
    assert MeshTerms().normalize_chemical(chemical) == expected







    



