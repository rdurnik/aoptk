import pytest
from aoptk.normalization.provide_mesh_term_dataframe_from_xml import ProvideMeshTermDataframeFromXML
from aoptk.normalization.provide_normalization_dataframe import ProvideNormalizationDataframe


@pytest.fixture
def provider() -> ProvideMeshTermDataframeFromXML:
    """Fixture providing a ProvideMeshTermDataframeFromXML instance."""
    return ProvideMeshTermDataframeFromXML(database_path="tests/test-data/test_mesh_term_database.xml")


def test_can_create():
    """Test that ProvideMeshTermDataframeFromXML can be instantiated."""
    actual = ProvideMeshTermDataframeFromXML(None)
    assert actual is not None


def test_implements_interface():
    """Test that ProvideMeshTermDataframeFromXML implements ProvideNormalizationDataframe interface."""
    assert issubclass(ProvideMeshTermDataframeFromXML, ProvideNormalizationDataframe)


def test_provide_normalization_dataframe_not_empty(provider: ProvideMeshTermDataframeFromXML):
    """Test that provide_normalization_dataframe method returns a non-empty DataFrame."""
    actual = provider.provide_normalization_dataframe()
    assert actual is not None


def test_extract_heading(provider: ProvideMeshTermDataframeFromXML):
    """Test extraction of heading from the normalization dataframe."""
    actual = provider.provide_normalization_dataframe()
    result = actual[actual["heading"] == "calcimycin"]["heading"].iloc[0]
    assert result == "calcimycin"


def test_extract_mesh_terms(provider: ProvideMeshTermDataframeFromXML):
    """Test extraction of MeSH terms from the normalization dataframe."""
    actual = provider.provide_normalization_dataframe()
    result = actual[actual["heading"] == "calcimycin"]["mesh_terms"].iloc[0]
    expected = [
        "4-benzoxazolecarboxylic acid, 5-(methylamino)-2-((3,9,11-trimethyl-8-(1-methyl-2-oxo-2-(1h-pyrrol-2-yl)ethyl)-"
        "1,7-dioxaspiro(5.5)undec-2-yl)methyl)-, (6s-(6alpha(2s*,3s*),8beta(r*),9beta,11alpha))-",
        "a-23187",
        "a 23187",
        "antibiotic a23187",
        "a23187, antibiotic",
        "a23187",
    ]
    assert result == expected
