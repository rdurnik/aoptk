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
    ("pubmed_id", "expected"),
    [
        (
            "41107038",
            [
                "https://gut.bmj.com/content/gutjnl/75/2/326.full.pdf",
                "https://gut.bmj.com/content/75/2/326.full.pdf",
                "https://gut.bmj.com/content/gutjnl/early/2025/10/16/gutjnl-2025-336400.full.pdf",
            ],
        ),
        ("26733159", ["https://www.degruyter.com/document/doi/10.1515/hsz-2015-0265/pdf"]),
    ],
)
@pytest.mark.xfail(raises=HTTPError)
def test_get_pubmed_url(pubmed_id: str, expected: str):
    """Test get pubmed url. Can result in 403 HHTP Error."""
    assert get_pubmed_pdf_url(pubmed_id) in expected
