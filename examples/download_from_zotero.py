"""Search your own Zotero library and download the publications it finds.

Runs against api.zotero.org when ``ZOTERO_LIBRARY_ID`` and ``ZOTERO_API_KEY`` are set, and
against the Zotero desktop app when ``ZOTERO_LOCAL=1`` (the app must be running with its local
API enabled, and then serves the library it is signed in to).

    export ZOTERO_SEARCH_TERM="hepg2 thioacetamide"
    export ZOTERO_LIBRARY_ID=1234567
    export ZOTERO_API_KEY=...           # needs the "library access" permission
    export ZOTERO_COLLECTION=ABCD1234   # optional, restricts the search to one collection
    uv run python examples/download_from_zotero.py

Writes the identifiers it finds to ids.txt and the full text of each publication to
publications/{id}.txt.
"""

import os
from pathlib import Path
from aoptk.literature.databases.zotero import Zotero
from aoptk.literature.query import Query

local = os.environ.get("ZOTERO_LOCAL") == "1"
search_term = os.environ.get("ZOTERO_SEARCH_TERM", "")

if not local and not (os.environ.get("ZOTERO_LIBRARY_ID") and os.environ.get("ZOTERO_API_KEY")):
    msg = "Set ZOTERO_LIBRARY_ID and ZOTERO_API_KEY, or ZOTERO_LOCAL=1 to use the desktop app."
    raise SystemExit(msg)

database = Zotero(
    storage=Path("./publications"),
    figure_storage=Path("./figures"),
    query=Query(search_term),
    library_id=os.environ.get("ZOTERO_LIBRARY_ID"),
    library_type=os.environ.get("ZOTERO_LIBRARY_TYPE", "user"),
    api_key=os.environ.get("ZOTERO_API_KEY"),
    collection=os.environ.get("ZOTERO_COLLECTION"),
    local=local,
)

# Zotero searches titles, creators and years; pass full_text_search=True to the constructor to
# search the text of the attached files as well. Query.full_text_subset is not available here.
ids = database.get_ids()

with Path("ids.txt").open("w") as f:
    f.writelines(f"{publication_id}{os.linesep}" for publication_id in ids)

publications = database.get_publications(ids, download_figures_enabled=False)
