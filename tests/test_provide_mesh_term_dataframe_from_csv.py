from aoptk.provide_normalization_dataframe import ProvideNormalizationDataframe
from aoptk.provide_mesh_term_dataframe_from_csv import ProvideMeshTermDataframeFromCSV
import pandas as pd
import pytest

def test_can_create():
    actual = ProvideMeshTermDataframeFromCSV(None)
    assert actual is not None

def test_implements_interface():
    assert issubclass(ProvideMeshTermDataframeFromCSV, ProvideNormalizationDataframe)

def test_provide_normalization_dataframe_not_empty():
    actual = ProvideMeshTermDataframeFromCSV(database_path='/home/rdurnik/aoptk/tests/test_mesh_terms_database.csv').provide_normalization_dataframe()
    assert actual is not None

def test_provide_normalization_dataframe_type():
    actual = ProvideMeshTermDataframeFromCSV(database_path = '/home/rdurnik/aoptk/tests/test_mesh_terms_database.csv').provide_normalization_dataframe()
    result = actual[actual['heading'] == 'acetaminophen']['mesh_terms'].iloc[0]
    expected = ['apap', 'acamol', 'acephen', 'acetaco', 'acetamidophenol', 'acetominophen', 'algotropyl', 'anacin 3', 'anacin-3', 'anacin3', 'datril', 'hydroxyacetanilide', 'n-(4-hydroxyphenyl)acetanilide', 'n-acetyl-p-aminophenol', 'panadol', 'paracetamol', 'tylenol', 'p-acetamidophenol', 'p-hydroxyacetanilide']
    assert result == expected
