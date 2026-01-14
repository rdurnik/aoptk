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


@pytest.fixture
def paracetamol() -> Chemical:
    """Fixture to create paracetamol chemical."""
    return Chemical("Paracetamol")


@pytest.fixture
def paracetamol_normalized(paracetamol: Chemical) -> Chemical:
    """Fixture to create normalized paracetamol."""
    paracetamol.heading = "acetaminophen"
    return paracetamol


def test_str(acetaminophen: Chemical):
    """Test __str__ function."""
    assert str(acetaminophen) == "acetaminophen"


def test_eq(acetaminophen: Chemical, thioacetamide: Chemical):
    """Testing comparison via __eq__ operator."""
    assert acetaminophen != thioacetamide
    assert acetaminophen == "acetaminophen"


def test_eq_heading(acetaminophen: Chemical, paracetamol_normalized: Chemical):
    """Test whether __eq__ respects heading and name order."""
    assert acetaminophen == paracetamol_normalized


def test_eq_similarity_synonyms(acetaminophen: Chemical, paracetamol: Chemical):
    """Test that chemicals with synonym matching given name are similar but not equal."""
    acetaminophen.synonyms.add("Paracetamol")
    assert acetaminophen != paracetamol
    assert acetaminophen.similar(paracetamol)


def test_name(acetaminophen: Chemical):
    """Test name."""
    assert acetaminophen.name == "acetaminophen"


def test_synonyms(acetaminophen: Chemical):
    """Test if synonyms can be manipulated correctly."""
    synonyms = {"Paracetamol", "4-Acetamidophenol", "103-90-2", "Tylenol"}
    acetaminophen.synonyms.update(synonyms)

    assert acetaminophen.synonyms == synonyms


def test_similarity(acetaminophen: Chemical):
    """Test chemical similarity."""
    paracetamol = Chemical("Paracetamol")
    assert not acetaminophen.similar(paracetamol)

    acetaminophen.synonyms.add("Paracetamol")
    assert acetaminophen.similar(paracetamol)
