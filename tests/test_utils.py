import pytest
from aoptk.utils import is_europepmc_id


@pytest.mark.parametrize(("id", "expected"), [
    ("123456", False),
    ("PMC123456", True),
])
def test_is_europepmc_id(id, expected):
    actual = is_europepmc_id(id)
    assert actual == expected
