from __future__ import annotations
from http.client import RemoteDisconnected
from pathlib import Path
import pytest
from requests import HTTPError
from aoptk.literature.databases.pmc import PMC
from aoptk.literature.get_pdf import GetPDF
from aoptk.literature.get_publication import GetPublication
from aoptk.literature.id import ID


def test_can_create(tmp_path_factory: pytest.TempPathFactory):
    """Test that EuropePMCPDF can be instantiated."""
    actual = PMC(
        "PMC8614944",
        storage=tmp_path_factory.mktemp("pmc_storage"),
        figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
    )
    assert actual is not None


def test_implements_interface():
    """Test that PymupdfParser implements GetPublication interface."""
    assert issubclass(PMC, GetPublication)
    assert issubclass(PMC, GetPDF)


def test_get_publication_data_not_empty(tmp_path_factory: pytest.TempPathFactory):
    """Test that pdfs() method returns non-empty list."""
    actual = PMC(
        "PMC8614944",
        storage=tmp_path_factory.mktemp("pmc_storage"),
        figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
    ).get_pdfs(ids=[])
    assert actual is not None


@pytest.mark.xfail(raises=HTTPError)
def test_open_access_pmc_pdf_file_exists(tmp_path_factory: pytest.TempPathFactory):
    """Test that an open access PMC PDF can be retrieved and saved."""
    storage_dir = tmp_path_factory.mktemp("pmc_storage")
    figure_storage_dir = tmp_path_factory.mktemp("pmc_storage_figures")
    PMC("PMC8614944", storage=storage_dir, figure_storage=figure_storage_dir).get_pdfs(ids=[ID("PMC8614944")])
    filepath = storage_dir / "PMC8614944.pdf"
    assert filepath.exists()
    assert filepath.is_file()
    assert filepath.stat().st_size > 0


@pytest.mark.xfail(raises=HTTPError)
def test_extract_full_text(provide_publications: dict, provide_temp_storage: Path, provide_temp_storage_figures: Path):
    """Test extracting full text."""
    actual = (
        PMC(query="queryblank", storage=provide_temp_storage, figure_storage=provide_temp_storage_figures)
        .get_publications(ids=[provide_publications["id"]])[0]
        .full_text
    )
    expected = provide_publications["full_text"]
    assert actual == expected


@pytest.mark.xfail(raises=HTTPError)
def test_get_id_small_query(tmp_path_factory: pytest.TempPathFactory):
    """Test that get_id() method returns a list of publication IDs."""
    actual = PMC(
        query="PMC12416454",
        storage=tmp_path_factory.mktemp("pmc_storage"),
        figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
    ).id_list
    expected = ["PMC12416454"]
    assert actual == expected


@pytest.mark.xfail(raises=(HTTPError, RemoteDisconnected))
def test_get_id_large_query(tmp_path_factory: pytest.TempPathFactory):
    """Test that get_id() method returns a list of publication IDs."""
    actual = len(
        PMC(
            query="methotrexate OR thioacetamide AND cancer AND fibrosis 1940/01/01:2023/01/30[epdat]",
            storage=tmp_path_factory.mktemp("pmc_storage"),
            figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
        ).id_list,
    )
    expected = 10101
    assert actual == pytest.approx(expected, abs=100)


@pytest.mark.xfail(raises=HTTPError)
def test_get_publications_wrong_ids_empty(tmp_path_factory: pytest.TempPathFactory):
    """Test that get_publications() method returns an empty list when given wrong IDs."""
    sut = PMC(
        query="queryblank",
        storage=tmp_path_factory.mktemp("pmc_storage"),
        figure_storage=tmp_path_factory.mktemp("pmc_storage_figures"),
    )

    actual = sut.get_publications([ID("invalid_id")])
    assert actual == []


@pytest.mark.xfail(raises=HTTPError)
def test_figures_not_being_downloaded(
    provide_publications: dict,
    provide_temp_storage: Path,
    provide_temp_storage_figures: Path,
):
    """Test that figures are not downloaded when download_figures_enabled is False."""
    actual = (
        PMC(query="queryblank", storage=provide_temp_storage, figure_storage=provide_temp_storage_figures)
        .get_publications(ids=[provide_publications["id"]], download_figures_enabled=False)[0]
        .figures
    )
    expected: list = []
    assert actual == expected
