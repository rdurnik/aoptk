import pytest
from aoptk.literature.id import DOI
from aoptk.literature.id import ID
from aoptk.literature.id import PMCID
from aoptk.literature.id import PMID
from aoptk.literature.metadata import Metadata


@pytest.mark.parametrize(
    ("metadata", "other", "expected_result"),
    [
        (
            Metadata(id=ID("PMC12345"), pmcid=PMCID("PMC12345"), pmid=None, doi=None),
            Metadata(id=ID("PMC12345"), pmcid=PMCID("PMC12345"), pmid=None, doi=None),
            True,
        ),
        (
            Metadata(id=ID("PMC12345"), pmcid=PMCID("PMC12345"), pmid=PMID("345678"), doi=None),
            Metadata(id=ID("345678"), pmcid=None, pmid=PMID("345678"), doi=None),
            True,
        ),
        (
            Metadata(id=ID("PMC12345"), pmcid=PMCID("PMC12345"), pmid=None, doi=None),
            Metadata(id=ID("PMC890345"), pmcid=PMCID("PMC890345"), pmid=None, doi=DOI("10.1000/xyz345")),
            False,
        ),
    ],
)
def test_eq(metadata: Metadata, other: Metadata, expected_result: bool):
    """Testing comparison via __eq__ operator."""
    assert (metadata == other) == expected_result
