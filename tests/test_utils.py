import shutil
from pathlib import Path
import pytest
from aoptk.literature.id import ID
from aoptk.literature.utils import convert_image_format
from aoptk.literature.utils import remove_pmc_prefix


@pytest.mark.parametrize(
    ("image_paths", "expected_paths", "expected_size"),
    [
        ([Path("tests/test_data/test_figures/gjic.jpeg")], [Path("tests/test_data/test_figures/gjic.png")], 139459),
        (
            [Path("tests/test_data/test_figures/liver_fibrosis.png")],
            [Path("tests/test_data/test_figures/liver_fibrosis.png")],
            410773,
        ),
        (
            [Path("tests/test_data/test_figures/liver_fibrosis.png"), Path("tests/test_data/test_figures/gjic.jpeg")],
            [Path("tests/test_data/test_figures/liver_fibrosis.png"), Path("tests/test_data/test_figures/gjic.png")],
            550232,
        ),
    ],
)
def test_convert_image_format(tmp_path: Path, image_paths: list[Path], expected_paths: list[Path], expected_size: int):
    """Test converting images to a specified format using list inputs."""
    shutil.copytree(Path("tests/test_data/test_figures"), tmp_path, dirs_exist_ok=True)
    images_to_convert = [tmp_path / p.name for p in image_paths]
    actual = convert_image_format(images_to_convert, target_format="png")
    expected_image_paths = [tmp_path / p.name for p in expected_paths]
    actual_size = sum(f.stat().st_size for f in expected_image_paths)
    assert sorted(actual) == sorted(expected_image_paths)
    assert actual_size == pytest.approx(expected_size, rel=0.1)


def test_remove_pmc_prefix():
    """Test removing the 'PMC' prefix from a list of IDs."""
    ids = [ID("PMC12345"), ID("PMC67890")]
    expected = [ID("12345"), ID("67890")]
    actual = remove_pmc_prefix(ids)
    assert actual == expected
