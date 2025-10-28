from aoptk.provide_normalization_dataframe import ProvideNormalizationDataframe
from aoptk.provide_mesh_term_dataframe_from_xml import ProvideMeshTermDataframeFromXML
import pandas as pd
import pytest

def test_can_create():
    actual = ProvideMeshTermDataframeFromXML(None)
    assert actual is not None

def test_implements_interface():
    assert issubclass(ProvideMeshTermDataframeFromXML, ProvideNormalizationDataframe)

def test_provide_normalization_dataframe_not_empty():
    actual = ProvideMeshTermDataframeFromXML(database_path='/home/rdurnik/aoptk/tests/full_mesh_term_database.xml').provide_normalization_dataframe()
    assert actual is not None

def test_extract_heading():
    actual = ProvideMeshTermDataframeFromXML(database_path='/home/rdurnik/aoptk/tests/full_mesh_term_database.xml').provide_normalization_dataframe()
    result = actual[actual['heading'] == 'calcimycin']['heading'].iloc[0]
    assert result == 'calcimycin'

def test_extract_mesh_terms():
    actual = ProvideMeshTermDataframeFromXML(database_path='/home/rdurnik/aoptk/tests/full_mesh_term_database.xml').provide_normalization_dataframe()
    result = actual[actual['heading'] == 'calcimycin']['mesh_terms'].iloc[0]
    assert result == ['4-benzoxazolecarboxylic acid, 5-(methylamino)-2-((3,9,11-trimethyl-8-(1-methyl-2-oxo-2-(1h-pyrrol-2-yl)ethyl)-1,7-dioxaspiro(5.5)undec-2-yl)methyl)-, (6s-(6alpha(2s*,3s*),8beta(r*),9beta,11alpha))-', 'a-23187', 'a 23187', 'antibiotic a23187', 'a23187, antibiotic', 'a23187']
                                                    

