import pytest
from aoptk.chemical import Chemical


@pytest.fixture
def acetaminophen() -> Chemical:
    """Fixture to create acetaminophen chemical."""
    return Chemical("acetaminophen")


@pytest.fixture
def thioacetamide() -> Chemical:
    """Fixture to create thioacetamide chemical."""
    return Chemical("thioacetamide")


def test_str(acetaminophen: Chemical):
    """Test __str__ function."""
    assert str(acetaminophen) == "acetaminophen"


def test_eq(acetaminophen: Chemical, thioacetamide: Chemical):
    """Testing comparison via __eq__ operator."""
    assert acetaminophen != thioacetamide
    assert acetaminophen == "acetaminophen"


def test_name(acetaminophen: Chemical):
    """Test name."""
    assert acetaminophen.name == "acetaminophen"


def test_name_is_in_synonyms(acetaminophen: Chemical):
    """ Testing if synonyms is not empty and has at least the given name. """
    assert 'acetaminophen' in acetaminophen.synonyms

def test_synonyms_set(acetaminophen: Chemical):
    synonyms = set(['Paracetamol', '4-Acetamidophenol', '103-90-2', 'Tylenol'])
    acetaminophen.synonyms = synonyms

    assert acetaminophen.synonyms == synonyms.union(['acetaminophen'])

def test_similarity(acetaminophen: Chemical):
    paracetamol = Chemical('Paracetamol')
    assert acetaminophen.similar(paracetamol) == False

    acetaminophen.synonyms.add('Paracetamol')
    assert acetaminophen.similar(paracetamol)
