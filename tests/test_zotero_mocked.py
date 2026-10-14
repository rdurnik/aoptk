# ruff: noqa: ANN001, ANN002, ANN003, ANN202, ARG001, ARG002, D101, D102, D103, PLR2004, SLF001
import builtins
import sys
from pathlib import Path
from types import SimpleNamespace
import pymupdf
import pytest
from aoptk.literature.databases import zotero as zotero_module
from aoptk.literature.databases.zotero import Zotero
from aoptk.literature.get_abstract import GetAbstract
from aoptk.literature.get_id import GetID
from aoptk.literature.get_metadata import GetMetadata
from aoptk.literature.get_pdf import GetPDF
from aoptk.literature.get_publication import GetPublication
from aoptk.literature.id import ID
from aoptk.literature.query import Query

ITEMS = [
    {
        "key": "AAAAAAAA",
        "data": {
            "itemType": "journalArticle",
            "title": "Title A",
            "DOI": "10.1002/anie.202513902",
            "date": "2025-03-14",
            "abstractNote": "Abstract A",
            "extra": "PMID: 40785269\nPMCID: PMC12416454",
            "creators": [
                {"creatorType": "author", "lastName": "Doe", "firstName": "Jane Ann"},
                {"creatorType": "author", "name": "Consortium"},
                {"creatorType": "editor", "lastName": "Ed", "firstName": "X"},
            ],
        },
    },
    {"key": "BBBBBBBB", "data": {"itemType": "journalArticle", "title": "No ids", "date": "March 2024"}},
    {"key": "CCCCCCCC", "data": {"itemType": "attachment", "parentItem": "AAAAAAAA"}},
]


def _pdf_bytes(text: str) -> bytes:
    doc = pymupdf.open()
    doc.new_page().insert_text((72, 72), text)
    return doc.tobytes()


class FakeClient:
    def __init__(self, items=None):
        self.items = ITEMS if items is None else items
        self.calls = []
        self.fulltext_fails = False
        self.linked_path = None

    def top(self, **kwargs):
        self.calls.append(("top", kwargs))
        return self.items

    def collection_items_top(self, collection, **kwargs):
        self.calls.append(("collection", collection, kwargs))
        return self.items

    def everything(self, query):
        return query

    def item(self, key):
        raise OSError

    def children(self, key):
        self.calls.append(("children", key))
        if key == "AAAAAAAA":
            return [
                {"key": "PDFKEY01", "data": {"itemType": "attachment", "contentType": "application/pdf"}},
                {"key": "IMGKEY01", "data": {"itemType": "attachment", "filename": "fig.png"}},
            ]
        if key == "LINKED01":
            return [
                {
                    "key": "LINKPDF1",
                    "data": {
                        "itemType": "attachment",
                        "linkMode": "linked_file",
                        "path": f"AbsoluteLink:{self.linked_path}",
                        "filename": "paper.pdf",
                    },
                },
            ]
        if key == "SECOND0002":
            return [{"key": "PDFKEY02", "data": {"itemType": "attachment", "contentType": "application/pdf"}}]
        return []

    def fulltext_item(self, key):
        self.calls.append(("fulltext", key))
        if self.fulltext_fails:
            raise OSError
        return {"content": "indexed text"}

    def file(self, key):
        return _pdf_bytes("pdf text") if key in ("PDFKEY01", "PDFKEY02", "LINKPDF1") else b""


@pytest.fixture
def fake(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(zotero_module, "_build_client", lambda *_: client)
    return client


@pytest.fixture
def make_zotero(monkeypatch):
    """Build a Zotero database backed by a FakeClient serving the given items."""

    def _make(tmp_path, items=None, **kwargs):
        client = FakeClient(items)
        monkeypatch.setattr(zotero_module, "_build_client", lambda *_: client)
        kwargs.setdefault("library_id", 1)
        return Zotero(tmp_path / "s", tmp_path / "f", Query("cadmium"), **kwargs), client

    return _make


@pytest.fixture
def zotero(fake, tmp_path):
    return Zotero(tmp_path / "s", tmp_path / "f", Query("cadmium"), library_id=1)


def test_implements_interface(zotero):
    for interface in (GetID, GetMetadata, GetAbstract, GetPDF, GetPublication):
        assert isinstance(zotero, interface)


def test_validation(fake, tmp_path):
    with pytest.raises(ValueError, match="library_id"):
        Zotero(tmp_path, tmp_path)
    with pytest.raises(ValueError, match="group"):
        Zotero(tmp_path, tmp_path, local=True, library_type="group")
    Zotero(tmp_path, tmp_path, local=True)


def test_missing_dependency(monkeypatch, tmp_path):
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "pyzotero":
            raise ImportError
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(ImportError, match=r"aoptk\[zotero\]"):
        Zotero(tmp_path, tmp_path, library_id=1)


def test_build_search_term(fake, tmp_path):
    assert Zotero(tmp_path, tmp_path, Query("a"), library_id=1).build_search_term(Query("a"))[1] == {
        "q": "a",
        "qmode": "titleCreatorYear",
    }
    z = Zotero(tmp_path, tmp_path, Query("a"), library_id=1, full_text_search=True)
    assert z._search_kwargs["qmode"] == "everything"
    for bad in (
        Query("a", full_text_subset=True),
        Query("a", only_preprint=True),
        Query("a", exclude_preprint=True),
        Query("a", licensing="CC0"),
        Query("a", date=("2020", "1", "1")),
    ):
        with pytest.raises(NotImplementedError):
            z.build_search_term(bad)


def test_get_ids(zotero, fake):
    assert zotero.get_ids() == [ID("10.1002/anie.202513902"), ID("BBBBBBBB")]
    assert fake.calls == [("top", {"q": "cadmium", "qmode": "titleCreatorYear"})]


def test_collection_scope(fake, tmp_path):
    Zotero(tmp_path, tmp_path, Query("x"), library_id=1, collection="COLL0001").get_ids()
    assert fake.calls[0][0] == "collection"


def test_metadata(zotero):
    first, second = zotero.get_publications_metadata(zotero.get_ids())
    assert first.pmid == "40785269"
    assert first.pmcid == "PMC12416454"
    assert first.year == 2025
    assert first.authors == ["Doe J.A.", "Consortium"]
    assert second.year == 2024
    assert second.authors is None


def test_resolve_by_pmid(zotero):
    assert len(zotero.get_publications_metadata([ID("40785269"), ID("unknown")])) == 1


def test_abstracts(zotero):
    abstracts = zotero.get_abstracts(zotero.get_ids())
    assert [a.text for a in abstracts] == ["Abstract A"]
    assert (zotero.storage / "10.1002_anie.202513902.txt").exists()


def test_pdfs(zotero):
    pdfs = zotero.get_pdfs([ID("BBBBBBBB"), ID("40785269")])
    assert len(pdfs) == 1
    assert Path(pdfs[0].path).read_bytes().startswith(b"%PDF")


def test_publications_fulltext(zotero):
    publication = zotero.get_publications([ID("40785269")], download_figures_enabled=False)[0]
    assert publication.full_text == "indexed text"
    assert publication.tables == []


def test_publications_fallback_to_pdf(zotero, fake):
    fake.fulltext_fails = True
    publication = zotero.get_publications([ID("40785269")], download_figures_enabled=False)[0]
    assert "pdf text" in publication.full_text


def test_publications_skip_items_without_full_text(make_zotero, tmp_path):
    """An item without a PDF attachment contributes no publication, not an empty one."""
    zotero, _ = make_zotero(tmp_path, items=[{"key": "NOCHILD0", "data": {"itemType": "journalArticle"}}])
    assert zotero.get_publications(zotero.get_ids()) == []


SECOND_ITEM = {"key": "SECOND0002", "data": {"itemType": "journalArticle", "title": "Second"}}
SECOND_IDS = [ID("40785269"), ID("SECOND0002")]


def _fulltext_calls(fake):
    return [call[1] for call in fake.calls if call[0] == "fulltext"]


def test_fulltext_asked_once_per_library_locally(make_zotero, tmp_path):
    """A local API without a full-text index should not be asked again for every item."""
    zotero, fake = make_zotero(tmp_path, items=[*ITEMS, SECOND_ITEM], local=True)
    fake.fulltext_fails = True
    assert len(zotero.get_publications(SECOND_IDS, download_figures_enabled=False)) == 2
    assert _fulltext_calls(fake) == ["PDFKEY01"]


def test_fulltext_asked_again_for_remote_libraries(make_zotero, tmp_path):
    """A remote failure can be transient, so every item keeps its own chance at the index."""
    zotero, fake = make_zotero(tmp_path, items=[*ITEMS, SECOND_ITEM])
    fake.fulltext_fails = True
    assert len(zotero.get_publications(SECOND_IDS, download_figures_enabled=False)) == 2
    assert _fulltext_calls(fake) == ["PDFKEY01", "PDFKEY02"]


def test_children_fetched_once_per_item(make_zotero, tmp_path):
    """Metadata, PDFs and the publication of one item must share a single children() call."""
    zotero, fake = make_zotero(tmp_path)
    ids = [ID("40785269")]
    zotero.get_publications_metadata(ids)
    zotero.get_pdfs(ids)
    zotero.get_publications(ids, download_figures_enabled=False)
    assert [call for call in fake.calls if call[0] == "children"] == [("children", "AAAAAAAA")]


def test_linked_file_pdf_is_read_from_disk(make_zotero, tmp_path):
    """Linked attachments live outside the library and are reported with an AbsoluteLink prefix."""
    source = tmp_path / "outside.pdf"
    source.write_bytes(_pdf_bytes("linked text"))
    item = {"key": "LINKED01", "data": {"itemType": "journalArticle", "title": "Linked", "DOI": "10.1/linked"}}
    zotero, fake = make_zotero(tmp_path, items=[item])
    fake.linked_path = source
    pdfs = zotero.get_pdfs([ID("10.1/linked")])
    assert len(pdfs) == 1
    assert Path(pdfs[0].path).read_bytes().startswith(b"%PDF")


def test_linked_file_missing_on_disk_is_skipped(make_zotero, tmp_path):
    """A linked file the user moved away must not abort the whole download."""
    item = {"key": "LINKED01", "data": {"itemType": "journalArticle", "title": "Linked", "DOI": "10.1/linked"}}
    zotero, fake = make_zotero(tmp_path, items=[item])
    fake.linked_path = tmp_path / "gone.pdf"
    assert zotero.get_pdfs([ID("10.1/linked")]) == []


def test_build_client_passes_credentials(monkeypatch):
    """The library coordinates, its type, the key and the endpoint reach pyzotero."""
    recorded = {}

    class Stub:
        def __init__(self, **kwargs):
            recorded.update(kwargs)

    monkeypatch.setitem(sys.modules, "pyzotero", SimpleNamespace(Zotero=Stub))
    zotero_module._build_client("42", "group", "secret", False)
    assert recorded == {"library_id": "42", "library_type": "group", "api_key": "secret", "local": False}
