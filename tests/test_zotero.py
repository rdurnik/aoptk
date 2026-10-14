"""Integration tests that read a real Zotero library.

What a user's own library contains is nobody's business but theirs, so these tests assert the
shape of the results - identifiers resolve, metadata matches the item it came from, stored
files are readable - rather than the presence of particular articles. Article-specific
expectations live in ``tests/test_zotero_mocked.py``, which drives a fixture library.

Two kinds of gating apply (see ``tests/service_availability.py``):

- the remote tests need api.zotero.org plus ``ZOTERO_LIBRARY_ID`` and ``ZOTERO_API_KEY``,
- the local tests need the Zotero desktop app running with its local API enabled, and are
  opted into with ``AOPKT_TEST_ZOTERO_LOCAL=1``.

Run them with ``uv run pytest tests/test_zotero.py -v``; without the above they skip.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Literal
import pytest
from aoptk.literature.databases.zotero import Zotero
from aoptk.literature.query import Query
from tests.service_availability import require_zotero_library
from tests.service_availability import require_zotero_local_service
from tests.service_availability import require_zotero_service

# ruff: noqa: PLR2004

LibraryType = Literal["user", "group"]


def _search_term() -> str:
    """Term to search for; empty means everything in the library or collection."""
    return os.getenv("ZOTERO_SEARCH_TERM", "")


def _collection() -> str | None:
    """Key of the collection to search, which keeps the run small on a large library."""
    return os.getenv("ZOTERO_COLLECTION")


def _library_type() -> LibraryType:
    """Library type named by the environment, rejected early if it is not one Zotero knows."""
    value = os.getenv("ZOTERO_LIBRARY_TYPE", "user")
    if value == "user":
        return "user"
    if value == "group":
        return "group"
    msg = f"ZOTERO_LIBRARY_TYPE must be 'user' or 'group', not {value!r}"
    raise ValueError(msg)


def _assert_ids_round_trip(database: Zotero) -> None:
    """Every identifier handed out by get_ids() resolves back to exactly one item."""
    ids = database.get_ids()
    assert len(ids) > 0
    assert [metadata.id for metadata in database.get_publications_metadata(ids)] == ids


def _assert_abstracts_are_stored(database: Zotero) -> None:
    """Abstracts are returned and their text written into the storage directory.

    Files are named after a sanitised identifier - a DOI contains path separators - so the
    text itself is what ties an abstract back to the file on disk.
    """
    abstracts = database.get_abstracts(database.get_ids())
    stored_text = {path.read_text(encoding="utf-8") for path in database.storage.glob("*.txt")}
    for abstract in abstracts:
        assert abstract.text.strip()
        assert abstract.text in stored_text


class TestRemoteLibrary:
    """Tests against a library on api.zotero.org, named by the environment."""

    @pytest.fixture(autouse=True)
    def require_remote(self) -> None:
        """Require the service and a configured library before each test of this class."""
        require_zotero_service()
        require_zotero_library()

    @pytest.fixture
    def database(self, tmp_path: Path) -> Zotero:
        """Database over the library the environment names."""
        return Zotero(
            tmp_path / "storage",
            tmp_path / "figures",
            Query(_search_term()),
            library_id=os.environ["ZOTERO_LIBRARY_ID"],
            library_type=_library_type(),
            api_key=os.environ["ZOTERO_API_KEY"],
            collection=_collection(),
        )

    def test_ids_round_trip(self, database: Zotero) -> None:
        """Every hit carries an identifier the same instance can look up again."""
        _assert_ids_round_trip(database)

    def test_metadata_is_usable(self, database: Zotero) -> None:
        """Metadata carries the identifier it was found under and a plausible year."""
        metadata_list = database.get_publications_metadata(database.get_ids())
        assert metadata_list
        for metadata in metadata_list:
            assert str(metadata.id)
            if metadata.year is not None:
                assert 1000 < metadata.year < 2200

    def test_abstracts_are_stored(self, database: Zotero) -> None:
        """Abstracts reach the storage directory."""
        _assert_abstracts_are_stored(database)

    def test_publications_have_full_text(self, database: Zotero) -> None:
        """Full text comes through for the items that have an attachment indexed by Zotero."""
        publications = database.get_publications(database.get_ids(), download_figures_enabled=False)
        stored_text = {path.read_text(encoding="utf-8") for path in database.storage.glob("*.txt")}
        for publication in publications:
            assert publication.full_text.strip()
            assert publication.full_text in stored_text
            # Zotero has no full-text XML, so these stay empty whatever the library holds.
            assert publication.tables == []
            assert publication.figure_descriptions == []


@pytest.mark.zotero_local
class TestLocalLibrary:
    """Tests against the Zotero desktop app running on this machine."""

    @pytest.fixture(autouse=True)
    def require_local(self) -> None:
        """Require the opt-in flag and a reachable local API before each test of this class."""
        require_zotero_local_service()

    @pytest.fixture
    def database(self, tmp_path: Path) -> Zotero:
        """Database over the library the desktop app is signed in to."""
        return Zotero(
            tmp_path / "storage",
            tmp_path / "figures",
            Query(_search_term()),
            local=True,
            collection=_collection(),
        )

    def test_ids_round_trip(self, database: Zotero) -> None:
        """The signed-in user's library is searchable through the local API."""
        _assert_ids_round_trip(database)

    def test_abstracts_are_stored(self, database: Zotero) -> None:
        """Abstracts reach the storage directory through the local API as well."""
        _assert_abstracts_are_stored(database)
