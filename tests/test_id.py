import pytest
from aoptk.literature.id import ID


@pytest.fixture
def publication_id() -> ID:
    """Fixture to create ID."""
    return ID("PMC12345")


def test_str(publication_id: ID):
    """Test __str__ function."""
    assert str(publication_id) == "PMC12345"


def test_eq(publication_id: ID):
    """Testing comparison via __eq__ operator."""
    assert publication_id == "PMC12345"
