"""Read literature from a Zotero library (zotero.org or the local desktop app).

Requires the optional dependency ``pyzotero`` (``pip install aoptk[zotero]``).

Example for the local desktop app (Zotero must be running with the local API enabled)::

    Zotero(storage, figure_storage, Query("cadmium"), local=True)
"""

from __future__ import annotations
import re
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Literal
import pymupdf
from aoptk.literature.abstract import Abstract
from aoptk.literature.get_abstract import GetAbstract
from aoptk.literature.get_id import GetID
from aoptk.literature.get_metadata import GetMetadata
from aoptk.literature.get_pdf import GetPDF
from aoptk.literature.get_publication import GetPublication
from aoptk.literature.id import DOI
from aoptk.literature.id import ID
from aoptk.literature.id import PMCID
from aoptk.literature.id import PMID
from aoptk.literature.metadata import Metadata
from aoptk.literature.pdf import PDF
from aoptk.literature.publication import Publication
from aoptk.literature.query import Query
from aoptk.literature.utils import convert_image_format

if TYPE_CHECKING:
    from collections.abc import Callable
    from pyzotero import Zotero as PyZotero

try:
    from pyzotero.errors import PyZoteroError

    _ZOTERO_ERRORS: tuple[type[BaseException], ...] = (PyZoteroError, OSError)
except ImportError:  # pragma: no cover - depends on the optional dependency
    _ZOTERO_ERRORS = (OSError,)

_ITEM_KEY_PATTERN = re.compile(r"^[0-9A-Z]{8}$")
_NON_PUBLICATION_TYPES = ("attachment", "note", "annotation")
_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif")
# Linked attachments are reported as "AbsoluteLink:/p/paper.pdf" or "relativeLink:paper.pdf";
# the alternatives are spelled out so that a Windows drive letter ("C:") is never mistaken
# for such a prefix.
_LINKED_PATH_PREFIX = re.compile(r"^(?:[a-z]*link|linkedfile):", re.IGNORECASE)


def _build_client(
    library_id: str | int,
    library_type: str,
    api_key: str | None,
    local: bool,
) -> PyZotero:
    """Create a pyzotero client, importing the optional dependency lazily.

    Kept as a separate function so that the module stays importable - and the
    class testable - without ``pyzotero`` installed.

    Args:
        library_id (str | int): Zotero library ID.
        library_type (str): Type of the library, "user" or "group".
        api_key (str | None): Zotero API key; None for public libraries and the local API.
        local (bool): Talk to the local desktop app instead of api.zotero.org.
    """
    try:
        from pyzotero import Zotero  # noqa: PLC0415
    except ImportError as error:
        msg = "Zotero support requires the optional dependency pyzotero - install it with `pip install aoptk[zotero]`."
        raise ImportError(msg) from error
    return Zotero(library_id=library_id, library_type=library_type, api_key=api_key, local=local)


class Zotero(GetID, GetMetadata, GetAbstract, GetPDF, GetPublication):
    """Class to get data from a Zotero library (local desktop app or zotero.org) based on a query.

    Only read operations are used; the library is never modified.
    """

    unified_image_format = "png"

    def __init__(  # noqa: PLR0913
        self,
        storage: Path,
        figure_storage: Path,
        query: Query | None = None,
        *,
        library_id: str | int | None = None,
        library_type: Literal["user", "group"] = "user",
        api_key: str | None = None,
        collection: str | None = None,
        local: bool = False,
        full_text_search: bool = False,
    ) -> None:
        """Initialize the Zotero database.

        Args:
            storage (Path): Directory for downloaded PDFs and texts.
            figure_storage (Path): Directory for figures.
            query (Query | None): Query used to search the library.
            library_id (str | int | None): Zotero library ID. Required for the remote API, defaults to 0 locally.
            library_type (Literal["user", "group"]): Type of the library. Groups only work with the remote API.
            api_key (str | None): Zotero API key (optional for public libraries and the local API).
            collection (str | None): Key of a collection to restrict the search to.
            local (bool): Use the local Zotero desktop API instead of api.zotero.org.
            full_text_search (bool): Also search inside the full text of attachments. Set this
                instead of ``Query.full_text_subset``, which Zotero does not support.
        """
        if not query:
            query = Query(search_term="")
        if local and library_type == "group":
            msg = "The local Zotero API only serves the local user library, not group libraries."
            raise ValueError(msg)
        if library_id is None:
            if not local:
                msg = "library_id is required when using the remote Zotero API."
                raise ValueError(msg)
            library_id = 0
        self.full_text_search = full_text_search
        self.local = local
        self.search_term, self._search_kwargs = self.build_search_term(query)
        self.storage = Path(storage)
        self.figure_storage = Path(figure_storage)
        self.storage.mkdir(parents=True, exist_ok=True)
        self.figure_storage.mkdir(parents=True, exist_ok=True)
        self.collection = collection
        self._client = _build_client(library_id, library_type, api_key, local)
        self._items: list[dict] | None = None
        self._child_cache: dict[str, list[dict]] = {}
        self._fulltext_unsupported = False

    def build_search_term(self, query: Query) -> tuple[str, dict]:
        """Convert a Query to the Zotero search term and search parameters.

        Zotero knows neither full-text subsets, preprints, licences nor date
        ranges, so queries that ask for them are rejected rather than silently
        returning the wrong set of items.

        Args:
            query (Query): Query to convert.

        Returns:
            tuple[str, dict]: The search term and the keyword arguments for the pyzotero search.
        """
        for name in ("full_text_subset", "only_preprint", "exclude_preprint", "licensing", "date"):
            if getattr(query, name):
                msg = f"The '{name}' filter is not available in Zotero."
                raise NotImplementedError(msg)
        kwargs: dict = {}
        if query.search_term:
            kwargs["q"] = query.search_term
            kwargs["qmode"] = "everything" if self.full_text_search else "titleCreatorYear"
        return query.search_term, kwargs

    def get_ids(self) -> list[ID]:
        """Get IDs (DOI, PMID, PMCID or Zotero item key) of the publications matching the query."""
        return [_get_publication_id(item) for item in self._get_scoped_items()]

    def get_publications_metadata(self, ids: list[ID]) -> list[Metadata]:
        """Retrieve publication metadata."""
        metadata = []
        for item in self._resolve(ids):
            data = item["data"]
            extra = data.get("extra", "")
            doi = data.get("DOI")
            pmid = _extract_identifier(extra, "PMID")
            pmcid = _extract_identifier(extra, "PMCID")
            year = _get_year(data.get("date", ""))
            metadata.append(
                Metadata(
                    id=_get_publication_id(item),
                    doi=DOI(doi) if doi else None,
                    pmid=PMID(pmid) if pmid else None,
                    pmcid=PMCID(pmcid) if pmcid else None,
                    year=int(year) if year else None,
                    title=data.get("title") or None,
                    authors=_get_authors(data.get("creators", [])) or None,
                ),
            )
        return metadata

    def get_abstracts(self, ids: list[ID]) -> list[Abstract]:
        """Retrieve abstracts and write them to storage."""
        abstracts = []
        for item in self._resolve(ids):
            try:
                if not (text := item["data"].get("abstractNote")):
                    continue
                abstract = Abstract(_get_publication_id(item), text)
                (self.storage / _file_name(abstract.id, "txt")).write_text(text, encoding="utf-8")
                abstracts.append(abstract)
            except _ZOTERO_ERRORS:
                continue
        return abstracts

    def get_pdfs(self, ids: list[ID]) -> list[PDF]:
        """Retrieve the PDF attachments of the publications and store them as `{id}.pdf`."""
        pdfs = []
        for item in self._resolve(ids):
            publication_id = _get_publication_id(item)
            try:
                attachment = self._find_attachment(item, _is_pdf)
                if attachment and (content := self._read_attachment(attachment)) is not None:
                    path = self.storage / _file_name(publication_id, "pdf")
                    path.write_bytes(content)
                    pdfs.append(PDF(path))
            except _ZOTERO_ERRORS:
                continue
        return pdfs

    def get_publications(self, ids: list[ID], download_figures_enabled: bool = True) -> list[Publication]:
        """Retrieve publications including full text.

        The full text is Zotero's index of the PDF attachment where it has one, and the text
        extracted from the attachment itself otherwise - an attachment that was never
        indexed, or that is not a PDF Zotero could index, still yields its text this way.
        Tables and figure descriptions are not available from Zotero and stay empty.

        Args:
            ids (list[ID]): A list of publication IDs to retrieve.
            download_figures_enabled (bool): Whether to copy image attachments to the figure storage.
        """
        publications = []
        for item in self._resolve(ids):
            try:
                publication = self._get_publication(item, download_figures_enabled=download_figures_enabled)
            except _ZOTERO_ERRORS:
                continue
            if publication:
                (self.storage / _file_name(publication.id, "txt")).write_text(publication.full_text, encoding="utf-8")
                publications.append(publication)
        return publications

    def _get_publication(self, item: dict, *, download_figures_enabled: bool) -> Publication | None:
        """Build a Publication for an item, or None when no full text can be obtained.

        Args:
            item (dict): The Zotero item to convert.
            download_figures_enabled (bool): Whether to copy image attachments to the figure storage.
        """
        publication_id = _get_publication_id(item)
        abstract = Abstract(publication_id, item["data"].get("abstractNote", ""))
        pdf_attachment = self._find_attachment(item, _is_pdf)
        full_text = self._get_full_text(pdf_attachment) if pdf_attachment else ""
        if not full_text:
            return None
        figures = self._get_figures(item, publication_id) if download_figures_enabled else []
        return Publication(publication_id, abstract, full_text, [], figures, [])

    def _get_full_text(self, attachment: dict) -> str:
        """Return the text of an attachment, from Zotero's index or from the file itself.

        Args:
            attachment (dict): The attachment item to read.
        """
        if not self._fulltext_unsupported:
            try:
                if content := self._client.fulltext_item(attachment["key"]).get("content", ""):
                    return content
            except _ZOTERO_ERRORS:
                # An endpoint that does not serve the index at all - the local API may be
                # one, depending on the Zotero version - will not start serving it
                # halfway through a library, so stop asking. Remote failures may merely
                # be transient, so those keep being retried per item.
                self._fulltext_unsupported = self.local
        pdf_bytes = self._read_attachment(attachment)
        if not pdf_bytes:
            return ""
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
            return "\n".join(page.get_text() for page in document)

    def _get_figures(self, item: dict, publication_id: ID) -> list[Path]:
        """Copy the image attachments of an item to the figure storage as PNG.

        Args:
            item (dict): The Zotero item whose attachments to copy.
            publication_id (ID): Identifier the files are named after.
        """
        figures = []
        for index, attachment in enumerate(self._children(item)):
            data = attachment["data"]
            filename = data.get("filename", "")
            if data.get("itemType") != "attachment" or not filename.lower().endswith(_IMAGE_EXTENSIONS):
                continue
            content = self._read_attachment(attachment)
            if content is None:
                continue
            path = self.figure_storage / _file_name(publication_id, Path(filename).suffix.lower(), f"_{index}")
            path.write_bytes(content)
            figures.append(path)
        return convert_image_format(figures, self.unified_image_format)

    def _children(self, item: dict) -> list[dict]:
        """Return the child items of an item, fetched at most once per item.

        Args:
            item (dict): The Zotero item to list the children of.
        """
        if item["key"] not in self._child_cache:
            self._child_cache[item["key"]] = self._client.children(item["key"])
        return self._child_cache[item["key"]]

    def _find_attachment(self, item: dict, predicate: Callable[[dict], bool]) -> dict | None:
        """Return the first child attachment whose data matches a predicate.

        Args:
            item (dict): The Zotero item to search the attachments of.
            predicate (Callable[[dict], bool]): Receives the attachment data.

        Returns:
            dict | None: The matching attachment, or None if there is none.
        """
        for child in self._children(item):
            data = child["data"]
            if data.get("itemType") == "attachment" and predicate(data):
                return child
        return None

    def _read_attachment(self, attachment: dict) -> bytes | None:
        """Read the content of an attachment, from the local disk for linked files.

        Args:
            attachment (dict): The attachment item to read.

        Returns:
            bytes | None: The content, or None when a linked file is not readable.
        """
        data = attachment["data"]
        if data.get("linkMode") == "linked_file":
            linked = _linked_file_path(data)
            return linked.read_bytes() if linked is not None and linked.is_file() else None
        return self._client.file(attachment["key"])

    def _get_scoped_items(self) -> list[dict]:
        """Fetch (once) the top-level items of the library or collection matching the query.

        Returns:
            list[dict]: The items the query and the configured collection are about; child
                items are never part of this list because they are attachments, not publications.
        """
        if self._items is None:
            if self.collection:
                items = self._client.everything(
                    self._client.collection_items_top(self.collection, **self._search_kwargs),
                )
            else:
                items = self._client.everything(self._client.top(**self._search_kwargs))
            self._items = [
                item
                for item in items
                if not item["data"].get("parentItem") and item["data"].get("itemType") not in _NON_PUBLICATION_TYPES
            ]
        return self._items

    def _resolve(self, ids: list[ID]) -> list[dict]:
        """Map requested IDs to Zotero items, skipping the ones that cannot be found.

        Args:
            ids (list[ID]): Identifiers as handed out by :meth:`get_ids`.

        Returns:
            list[dict]: The items belonging to the requested identifiers.
        """
        index: dict[str, dict] = {}
        for item in self._get_scoped_items():
            # setdefault, so that the first item claiming an identifier wins - the
            # same item a linear search over the scoped items would have returned.
            for candidate in _identifier_candidates(item):
                index.setdefault(candidate, item)
        resolved = []
        for requested in ids:
            found = index.get(str(requested))
            if found is None and _ITEM_KEY_PATTERN.fullmatch(str(requested)):
                try:
                    found = self._client.item(str(requested))
                except _ZOTERO_ERRORS:
                    found = None
            if found is not None and found["data"].get("itemType") not in _NON_PUBLICATION_TYPES:
                resolved.append(found)
        return resolved


def _file_name(publication_id: ID, extension: str, suffix: str = "") -> str:
    """Build a file name from an ID; DOIs contain path separators that must be replaced.

    Args:
        publication_id (ID): Identifier the file is named after.
        extension (str): File extension, with or without a leading dot.
        suffix (str): Extra infix, used to keep several figures of one item apart.
    """
    extension = extension.lstrip(".")
    return f"{re.sub(r'[^A-Za-z0-9._-]', '_', str(publication_id))}{suffix}.{extension}"


def _is_pdf(data: dict) -> bool:
    """Return whether attachment data describes a PDF.

    Args:
        data (dict): The data of an attachment item.
    """
    return data.get("contentType") == "application/pdf" or data.get("filename", "").lower().endswith(".pdf")


def _identifier_candidates(item: dict) -> list[str]:
    """Return every identifier an item can be addressed by.

    Args:
        item (dict): The Zotero item to inspect.
    """
    data = item["data"]
    extra = data.get("extra", "")
    candidates = [data.get("DOI"), _extract_identifier(extra, "PMID"), _extract_identifier(extra, "PMCID")]
    if key := item.get("key") or data.get("key"):
        candidates.append(key)
    return [candidate for candidate in candidates if candidate]


def _linked_file_path(data: dict) -> Path | None:
    """Turn Zotero's linked-file reference into a filesystem path.

    Linked attachments are not stored inside the library; the API reports where the file
    lives as a scheme-like value such as ``AbsoluteLink:/home/me/paper.pdf``, or as a path
    relative to the directory kept in ``parentDir`` (``linkedFile:../papers/paper.pdf``).
    The prefix has to go before the value can be used as a path.

    Args:
        data (dict): The data of an attachment item.

    Returns:
        Path | None: The referenced location, or None if there is no usable reference.
    """
    raw = data.get("path")
    if not raw:
        return None
    path = Path(_LINKED_PATH_PREFIX.sub("", str(raw).strip(), count=1))
    # Path("") would silently mean "the current directory", which is never the intent.
    if not path.parts:
        return None
    if path.is_absolute():
        return path
    parent = data.get("parentDir")
    if not parent:
        return path
    # parentDir is itself reported in the prefixed form, so strip it the same way.
    return Path(_LINKED_PATH_PREFIX.sub("", str(parent).strip(), count=1)) / path


def _extract_identifier(extra: str, label: str) -> str | None:
    """Extract an identifier such as 'PMID: 123' from Zotero's free-text 'extra' field.

    Zotero has no dedicated PMID or PMCID field; its importers write them into 'extra'.

    Args:
        extra (str): The contents of the item's 'extra' field.
        label (str): Identifier to look for, e.g. 'PMID'.

    Returns:
        str | None: The identifier, or None if the field does not mention it.
    """
    match = re.search(rf"^\s*{label}\s*:\s*(\S+)", extra or "", flags=re.IGNORECASE | re.MULTILINE)
    return match.group(1) if match else None


def _get_publication_id(item: dict) -> ID:
    """Return the DOI, PMID, PMCID or Zotero key (in this order) of an item.

    Preferring the bibliographic identifiers over the Zotero key keeps the results
    interchangeable with the other databases of the package.

    Args:
        item (dict): The Zotero item to get the identifier of.
    """
    data = item["data"]
    extra = data.get("extra", "")
    publication_id = (
        data.get("DOI")
        or _extract_identifier(extra, "PMID")
        or _extract_identifier(extra, "PMCID")
        or item.get("key")
        or data.get("key")
    )
    if not publication_id:
        msg = "Zotero item is missing a publication id"
        raise ValueError(msg)
    return ID(publication_id)


def _get_year(date: str) -> str | None:
    """Return the year contained in a Zotero date, which is free text.

    Args:
        date (str): The item's 'date' field, e.g. '2025-03-14' or 'March 2025'.

    Returns:
        str | None: Four digits, or None if the field carries no year.
    """
    match = re.search(r"\d{4}", date or "")
    return match.group(0) if match else None


def _get_authors(creators: list[dict]) -> list[str]:
    authors = []
    for creator in creators:
        if creator.get("creatorType", "author") != "author":
            continue
        if last := creator.get("lastName"):
            initials = "".join(f"{part[0]}." for part in creator.get("firstName", "").replace("-", " ").split())
            authors.append(f"{last} {initials}".strip())
        elif name := creator.get("name"):
            authors.append(name)
    return authors
