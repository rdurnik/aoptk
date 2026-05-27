import shutil
from pathlib import Path
import pytest
from aoptk.literature.id import ID
from aoptk.literature.utils import convert_image_format
from aoptk.literature.utils import remove_pmc_prefix


def test_convert_image_format(tmp_path: Path):
    """Test converting images to a specified format."""
    shutil.copytree(Path("tests/test_data/test_figures"), tmp_path, dirs_exist_ok=True)
    actual = convert_image_format(list(tmp_path.iterdir()), target_format="png")
    expected = [tmp_path / "gjic.png", tmp_path / "liver_fibrosis.png"]
    total_size = sum(f.stat().st_size for f in tmp_path.iterdir())
    expected_size = 1375641
    assert actual == sorted(expected)
    assert total_size == pytest.approx(expected_size, rel=0.1)


def test_remove_pmc_prefix():
    """Test removing the 'PMC' prefix from a list of IDs."""
    ids = [ID("PMC12345"), ID("PMC67890")]
    expected = [ID("12345"), ID("67890")]
    actual = remove_pmc_prefix(ids)
    assert actual == expected
