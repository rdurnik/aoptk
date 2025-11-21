import pytest
from aoptk.chemical import Chemical


@pytest.fixture
def acetaminophen() -> Chemical:
    return Chemical("acetaminophen")

@pytest.fixture
def thioacetamide() -> Chemical:
    return Chemical('thioacetamide')

def test_str(acetaminophen: Chemical):
    """ Test __str__ function. """
    assert str(acetaminophen) == "acetaminophen"

def test_eq(acetaminophen: Chemical, thioacetamide: Chemical):
    """ Testing comparison via __eq__ operator. """
    assert acetaminophen != thioacetamide
    assert acetaminophen == acetaminophen

def test_name(acetaminophen: Chemical):
    """ Test name. """
    assert acetaminophen.name == 'acetaminophen'