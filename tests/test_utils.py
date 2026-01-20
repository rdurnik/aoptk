import pytest
from requests import HTTPError
from aoptk.literature.utils import get_pubmed_pdf_url
from aoptk.literature.utils import is_europepmc_id


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


@pytest.mark.parametrize(
    ("pubmed_id", "expected_doi"),
    [
        ("41107038", "10.1136/gutjnl-2025-336400"),
        ("26733159", "10.1515/hsz-2015-0265"),
    ],
)
@pytest.mark.xfail(raises=HTTPError)
def test_get_pubmed_url(pubmed_id: str, expected_doi: str):
    """Test get pubmed url.

    This test is marked as xfail because it requires network access to NCBI APIs,
    which may not be available in all testing environments. The function should
    return a DOI URL in the format https://doi.org/{doi} as a fallback when
    direct publisher PDF links are not available.
    """
    url = get_pubmed_pdf_url(pubmed_id)
    # The function should return either a PMC URL or a DOI URL
    assert url.startswith("https://europepmc.org/") or url == f"https://doi.org/{expected_doi}"
