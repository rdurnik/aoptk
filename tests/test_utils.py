import pytest
from aoptk.utils import is_europepmc_id, get_pubmed_pdf_url


@pytest.mark.parametrize(
    ("publication_id", "expected"),
    [
        ("123456", False),
        ("PMC123456", True),
    ],
)
def test_is_europepmc_id(publication_id: str, expected: bool):
    """Test the is_europepmc_id function."""
    actual = is_europepmc_id(publication_id)
    assert actual == expected


def test_get_pubmed_url():
    pubmed_id = '41107038'
    actual = get_pubmed_pdf_url(pubmed_id)
    
    assert actual == 'https://gut.bmj.com/content/gutjnl/early/2025/10/16/gutjnl-2025-336400.full.pdf'

