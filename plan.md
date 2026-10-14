# Plan: Zotero as a literature query and retrieval database ([#156](https://github.com/rdurnik/aoptk/issues/156))

**Phase:** Implementation planning (Research → *Plan* → Implement → Verify).
**Branch:** `hechth/issue156` (already checked out).
**Scope:** new read-only `Zotero` database backend in `src/aoptk/literature/databases/`, built on
[`pyzotero`](https://pyzotero.readthedocs.io/en/latest/), implementing the same interfaces as `EuropePMC`.

---

## 1. What the issue asks for

1. Use `pyzotero` so a user can point aoptk at **their own** Zotero library (local desktop app and/or
   `api.zotero.org` account) and search it for literature by implementing the `GetID` interface.
2. After search, return the publication **IDs** (e.g. DOI).
3. Then retrieve the **items and their full text** from Zotero
   ([full-text content endpoint](https://www.zotero.org/support/dev/web_api/v3/fulltext_content)).
4. API keys and collection details are supplied **as parameters to the database object**.

## 2. Decisions

Confirmed with the user:

| # | Decision | Choice |
|---|----------|--------|
| D1 | Backend | Both remote (`api.zotero.org`) and local desktop API (`127.0.0.1:23119`), selected by a `local: bool` flag |
| D2 | Interfaces | All five, like `EuropePMC`: `GetID`, `GetMetadata`, `GetAbstract`, `GetPDF`, `GetPublication` |
| D3 | Dependency | Optional extra `aoptk[zotero]` + lazy import inside the module |

Derived design decisions (reversible, but stated so the implementation is unambiguous):

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| D4 | Where does the search term come from? | Constructor `query: Query \| None`, exactly like `EuropePMC`/`PMC` | `GetID.get_ids(self)` takes **no** arguments (`src/aoptk/literature/get_id.py:14`); the search term must be state |
| D5 | Which items are in scope? | If `collection` given → that collection's top-level items, else the whole library's top-level items (`zot.top()`); attachments/notes are never returned as publications | Issue asks for "collection related details as parameter"; child items are attachments, not publications |
| D6 | ID preference order | `DOI` → `PMID` → `PMCID` → Zotero item key (as `ID`) | Issue says "IDs (e.g. DOI)"; DOI/PMID/PMCID keep results interoperable with `PMC`/`EuropePMC`; the Zotero key is the always-available fallback |
| D7 | PMID/PMCID source in Zotero | Parsed from the free-text `extra` field (`PMID: 123…`, `PMCID: PMC…`), DOI from `data["DOI"]` | Zotero has no dedicated PMID field; this is the convention Zotero's own importers write |
| D8 | Unsupported `Query` filters | `full_text_subset`, `only_preprint`, `exclude_preprint`, `licensing` and `date` → `NotImplementedError` | Mirrors `PubMed.build_search_term` raising for `licensing` (`src/aoptk/literature/databases/pubmed.py:46`). Zotero's Read API has no date/preprint/licence concepts. Client-side date filtering was implemented and then dropped: `Query.date` means a server-side search filter everywhere else, so filtering a fetched library client-side would quietly mean something different, and rejecting is the honest option. |
| D9 | `GetPublication` full text | Attachment full-text index via `zot.fulltext_item(key)`; on any failure (including `ResourceNotFoundError`) fall back to the attachment file + PyMuPDF text extraction | pyzotero exposes `fulltext_item`, and the Web API documents a per-item `GET …/fulltext`. Whether the local API serves it is version-dependent — its page claims most endpoints behave identically, which contradicts this plan's first reading — so the fallback exists because it is needed at least for unindexed and non-PDF attachments, and it covers the local case whatever the answer is. `pymupdf` is already a hard dependency. |
| D10 | Figures / tables in `GetPublication` | Images attached to the item → `list[Path]` normalised to PNG via the existing `convert_image_format`; `figure_descriptions=[]`, `tables=[]` | Zotero has no JATS XML, so `EuropePMC`'s XML parsing has no analogue; images cost nothing and feed the existing image pipeline |
| D11 | Search mode | Constructor flag `full_text_search: bool = False` → `qmode="everything"` instead of the default `titleCreatorYear` | Only way to search inside the library's full text; kept explicit so default behaviour is the cheap one |
| D12 | Writes to the library | None. Read-only methods only | aoptk consumes literature; mutating a user's library is out of scope and dangerous |

## 3. Verified background (do not re-derive)

- **`pyzotero` latest: 1.15.2** (uploaded 2026-09-18), `requires-python >= 3.10` (classifiers cover 3.11–3.14),
  so it fits the project's `requires-python = ">=3.11"`. Transitive deps: `feedparser`, `bibtexparser<2`,
  `whenever`, `httpx2`. Available on **conda-forge** (1.15.2); **not** on bioconda — another reason for D3.
- Constructor (read from the 1.15.2 wheel):
  `Zotero(library_id=None, library_type=None, api_key=None, preserve_json_order=False, locale="en-US", local=False, client=None, upload_timeout=120, server_id=None, local_api_key=None)`.
  `local=True` switches the endpoint to `http://127.0.0.1:23119/api`; missing id/type raises
  `MissingCredentialsError`; `api_key` is optional for public libraries.
- Methods used: `top(**kwargs)`, `items(**kwargs)`, `collection_items_top(collection, **kwargs)`,
  `children(itemkey)`, `item(itemkey)`, `fulltext_item(itemkey)` (→ `{"content": …, "indexedPages": …}`),
  `file(itemkey)` (→ raw `bytes`), `everything(query)` for pagination.
  **`dump()` returns `None` in 1.15.2** and names the file after the attachment's own filename → we write
  bytes ourselves so files land at `storage/{id}.pdf` (same convention as `EuropePMC._write_pdf`).
- Search kwargs: `q` plus `qmode` ∈ {`titleCreatorYear` (default), `everything`}. The `@retrieve`
  decorator resets `url_params` after every call, so **search kwargs must be passed on every call**.
- Rate limiting is handled inside pyzotero: HTTP 429 records a server-supplied backoff and retries up to
  `MAX_RETRY_ATTEMPTS`, then raises `pyzotero.errors.TooManyRetriesError`. We add no extra retry layer
  (unlike EuropePMC's `requests` adapter), and no artificial `sleep`.
- All pyzotero errors subclass `pyzotero.errors.PyZoteroError` (includes `ResourceNotFoundError`,
  `UserNotAuthorisedError`, `MissingCredentialsError`, `TooManyRetriesError`).
- **Local API constraints** ([docs](https://www.zotero.org/support/dev/web_api/v3/local_api)): Zotero must
  be running with the local API enabled; reads are unauthenticated; only the locally logged-in user is
  reachable (`library_id` → `0`), group ids return 400; no Atom; results are not paginated by default
  (`everything()` still works — it stops when there is no `next` link); `…/file` answers with a 302 to a
  `file://` URL, which pyzotero follows with its bundled `file://` transport.

## 4. Design

### 4.1 Public surface (`src/aoptk/literature/databases/zotero.py`, new)

```python
class Zotero(GetID, GetMetadata, GetAbstract, GetPDF, GetPublication):
    """Class to get data from a Zotero library (local desktop app or zotero.org) based on a query."""

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
    ) -> None: ...
```

- `def __init__(  # noqa: PLR0913` — verified against the repo's ruff config that 8 arguments are flagged
  **even when keyword-only**. Keeping the parameters flat is deliberate: the issue asks for the keys and
  collection details "as parameter to the database". (Alternative the maintainer may prefer:
  `[tool.ruff.lint.per-file-ignores] "src/aoptk/literature/databases/zotero.py" = ["PLR0913"]`.)
- Validation in `__init__`: `local=False` and `library_id is None` → `ValueError` with an actionable message;
  `local=True` and `library_type == "group"` → `ValueError` (local API serves only the local user).
  With `local=True` and `library_id is None`, default to `0`. `api_key` may stay `None` (public libraries).
- `storage` / `figure_storage` are `mkdir(parents=True, exist_ok=True)`d, and retrieved texts are written to
  `storage/{id}.txt`, matching `EuropePMC`/`PMC` so downstream examples work unchanged.
- `build_search_term(query) -> tuple[str, dict]` (or a private `_search_params`): returns the `q` string plus
  the kwargs dict (`qmode`) and raises `NotImplementedError` for the four unsupported flags (D8). Named
  `build_search_term` for symmetry with the other databases; `self.search_term` holds the `q` string so
  tests/debug output look familiar.

### 4.2 Lazy dependency loading

```python
def _build_client(library_id, library_type, api_key, local) -> "Zotero":
    try:
        from pyzotero import Zotero  # noqa: PLC0415
    except ImportError as error:
        msg = "Zotero support requires the optional dependency pyzotero - install it with `pip install aoptk[zotero]`."
        raise ImportError(msg) from error
    return Zotero(library_id=library_id, library_type=library_type, api_key=api_key, local=local)
```

- Import happens inside the function (verified: ruff accepts this with `# noqa: PLC0415`); the module itself
  must stay importable **without** pyzotero installed, otherwise `import aoptk` breaks for everyone.
- Exception types caught by retrieval loops: module-level
  `try: from pyzotero.errors import PyZoteroError; _ZOTERO_ERRORS = (PyZoteroError, OSError) / except ImportError: _ZOTERO_ERRORS = (OSError,)`.
  Mirrors the `except (HTTPError, MaxRetryError): continue` contract of `EuropePMC`, and stays testable without
  pyzotero installed (mocks raise `OSError` subclasses).

### 4.3 Interface → Zotero mapping

| Method | Zotero calls | Output |
|--------|--------------|--------|
| `get_ids()` | scoped items (`top`/`collection_items_top` with `q`, `qmode`) | `list[ID]` per D6 |
| `get_publications_metadata(ids)` | same scoped items (cached) | `Metadata(id, doi, pmid, pmcid, year, title, authors)`; `authors` = `"Family I.I."`/`name` strings from `data["creators"]`, `year` = first 4 digits of `data["date"]` |
| `get_abstracts(ids)` | `data["abstractNote"]` | `Abstract(id, text)`, skip when empty (as `EuropePMC` skips missing abstracts); written to `storage/{id}.txt` |
| `get_pdfs(ids)` | `children(key)` → attachment with `contentType == "application/pdf"` (or `.pdf` filename) → `file(key)` bytes, or copy for `linkMode == "linked_file"` | `[PDF(storage / f"{id}.pdf")]` |
| `get_publications(ids)` | metadata + `abstractNote` + full text (D9) + image attachments (D10) | `Publication(id, Abstract, full_text, tables=[], figures, figure_descriptions=[])`; written to `storage/{id}.txt` |

Shared internals:

- `_get_scoped_items()` — one fetch per instance, cached in `self._items`, filtered to top-level
  (`not data.get("parentItem")`, `itemType` not in `{"attachment", "note"}`), then the `Query.date`
  client-side filter (D8). `get_ids()` and the lookups below all go through it, so a search-then-download run
  makes exactly one item-list request.
- `_resolve(ids)` — map requested `ID`s to cached items; on miss, retry via `zot.item(key)` only if the ID
  matches Zotero's 8-character key pattern; unresolvable IDs are skipped (same tolerance as the other databases).
- `_get_attachment(item, predicate)` — locate a child attachment by content type / filename.
- Module-level helpers `_get_publication_id(item)`, `_extract_identifier(extra, label)`, `_get_year(date_str)`,
  `_get_authors(creators)` — small pure functions, the primary unit-test targets (pattern: `_get_publication_id`
  at `src/aoptk/literature/databases/europepmc.py:450`).

## 5. Implementation steps

Each step ends green on its own acceptance check.

1. **Dependency wiring** — `pyproject.toml`: add `zotero = ["pyzotero>=1.15.2"]` under
   `[project.optional-dependencies]`; register the new pytest marker `zotero_local` in
   `markers`. Run `uv lock` (CI runs `uv lock` then `uv sync --frozen`, so a stale `uv.lock` fails the build).
   *Check:* `uv sync --frozen --extra dev --extra zotero && uv run python -c "import pyzotero"`.
2. **Module skeleton + ID/metadata helpers** — new `src/aoptk/literature/databases/zotero.py` with the class,
   `__init__` validation, `_build_client`, and the pure helpers (ID preference order, `extra` parsing,
   year, authors, `build_search_term`/`NotImplementedError` rules). No network code yet.
   *Check:* `uv run ruff check src/aoptk && uv run mypy src/aoptk --show-error-codes`.
3. **`GetID` + `GetMetadata`** — scoping, pagination via `everything()`, caching, date filter.
   *Check:* mocked tests of step 7 pass.
4. **`GetAbstract` + `GetPDF`** — abstracts from `abstractNote`; PDF attachment download (stored + linked-file
   copy) written to `storage/{id}.pdf`, returning `PDF`.
   *Check:* mocked tests pass; `PymupdfParser(pdfs=…).get_publications()` accepts the produced `PDF` objects
   (proves interchangeability with the existing pipeline).
5. **`GetPublication`** — full text via `fulltext_item` with the PyMuPDF fallback (D9), image attachments
   normalised via `convert_image_format(..., "png")`, `storage/{id}.txt` written.
   *Check:* mocked tests pass; `docs` doctest build unaffected.
6. **Test fixtures + unit tests** (see §6).
   *Check:* `uv run pytest tests/test_zotero_mocked.py -v` passes **with pyzotero uninstalled as well as installed**.
7. **Integration tests + service gating** (see §6).
   *Check:* `uv run pytest tests/test_zotero.py -v` → passes or reports `xfail`/`skipped`, never `error`, in CI.
8. **Examples** — `examples/download_from_zotero.py` in the style of the existing scripts (env-driven:
   `ZOTERO_LIBRARY_ID`, `ZOTERO_LIBRARY_TYPE`, `ZOTERO_API_KEY`, `ZOTERO_COLLECTION`), showing
   `get_ids()` → `get_publications()`; a local-mode snippet in the module docstring.
   *Check:* `uv run python examples/download_from_zotero.py --help`-style smoke (guard the network call behind
   the same env-var checks the other examples rely on).
9. **Documentation** — `README.md`: add Zotero to the databases sentence and an "Use your own Zotero library"
   subsection with `pip install aoptk[zotero]`, remote and local usage; `.env.example`: the four Zotero
   variables; `README.dev.md`: how to run the gated tests (`--zotero-local` / env vars, Zotero must be running).
   Google-style docstrings on every public method so `sphinx-autoapi` picks them up.
   *Check:* `uv run make -C docs coverage doctest html` and `uv run cffconvert --validate` (unchanged → still valid).
10. **CI** — `.github/workflows/build.yml`: install with `--extra zotero` in the test job so the real import
    path is exercised; keep lint/typecheck jobs as they are (mypy already sets `ignore_missing_imports`).
    *Check:* `uv run python -m pytest -m "not openai and not zotero_local" -q` locally reproduces the CI set.
11. **Final verification** (§7) and commit split: `feat: read literature from a Zotero library`, `test: …`,
    `docs: …` — logically separated per the project's principles.

## 6. Testing plan

`pyzotero` will not be installed on most developer machines and never on a CI runner that only installs
`--extra dev`, so the load-bearing tests must be **mocked and pyzotero-free**.

**`tests/test_zotero_mocked.py` (new, always runs).** A `FakeZoteroClient` (plain Python object returning the
dicts from the fixture) injected by monkeypatching `aoptk.literature.databases.zotero._build_client`. Cases:

- `test_can_create`, `test_implements_interface` (all five ABCs — the convention in every `tests/test_*.py`).
- Constructor validation: remote without `library_id` → `ValueError`; `local=True` + `library_type="group"` →
  `ValueError`; `local=True` defaults `library_id` to `0`.
- Missing dependency path: monkeypatch `builtins.__import__` so `from pyzotero import Zotero` raises
  `ImportError`, assert our actionable message.
- `build_search_term`: plain term; `full_text_search=True` → `qmode="everything"`; each unsupported flag raises
  `NotImplementedError`.
- `get_ids` ID preference: DOI only / DOI+PMID / PMCID only / none → Zotero key; children filtered out.
- `get_publications_metadata`: DOI/PMID/PMCID parsed from `extra`, `year` from `"2025-03-14"`, `"March 2025"`,
  `""`; authors from `lastName`+`firstName`, and single-field `name` creators.
- `get_abstracts`: abstract written to `storage/{id}.txt`; item without `abstractNote` skipped.
- `get_pdfs`: stored-file attachment written to `storage/{id}.pdf`; `linked_file` copied; item without a PDF
  attachment skipped.
- `get_publications`: `fulltext_item` content used; on `OSError`-based failure the PyMuPDF fallback is used;
  image attachments converted to PNG.
- Pagination: fake client with `links["next"]` → all pages collected.
- Tolerance: a client raising `OSError` (and, when importable, `pyzotero.errors.PyZoteroError` guarded by
  `pytest.importorskip("pyzotero")`) → that ID skipped, the rest returned; and `get_ids()` re-raising a hard
  auth error rather than silently returning `[]`.

**`tests/test_zotero.py` (new, gated integration).** Real library, following
`tests/service_availability.py`'s xfail-on-outage convention:

- `require_zotero_service()` — probe `https://api.zotero.org`; module-level autouse fixture like
  `test_aop_wiki.py`'s; additionally `pytest.skip` unless `ZOTERO_LIBRARY_ID` + `ZOTERO_API_KEY` are set
  (secrets are not available in forks' CI, and an unauthenticated probe of a private library proves nothing).
- `pytest.mark.zotero_local` + `require_zotero_local_service()` probing `http://127.0.0.1:23119/api/users/0/items`,
  enabled only when `AOPKT_TEST_ZOTERO_LOCAL=1`; asserts `get_ids()` → `get_publications()` on the user's own library.
- Add the probes/helpers to `tests/service_availability.py` next to the existing `*_endpoints` tuples, and
  register `zotero_local` in `[tool.pytest.ini_options].markers`.

**Fixture data.** `tests/test_data/zotero_items.json` — a hand-written item list modelled on
`tests/test_data/europepmc_metadata.json`, carrying the *real* identifiers of the articles already used in the
suite (DOI `10.1002/anie.202513902`, PMID `40785269`, PMCID `PMC12416454`, …) so expectations stay honest and
cross-checkable against the live Europe PMC/PMC tests. Never invent identifiers.

## 7. Verification checklist

```console
uv lock && uv sync --frozen --extra dev --extra zotero
uv run python -m pytest -m "not openai" -v          # full suite, Zotero integration xfail/skip
uv run python -m pytest tests/test_zotero_mocked.py -v
uv run ruff check && uv run ruff format --check
uv run mypy src/aoptk tests --show-error-codes --pretty
uv run make -C docs coverage doctest html
uv run python -m build
```

Plus, with `pyzotero` **not** installed (`uv sync --frozen --extra dev`): `uv run python -c "import aoptk.literature.databases.zotero"`
must succeed and instantiating `Zotero(...)` must raise the actionable `ImportError`.

Issue completion criteria: requirements satisfied (search → IDs → items → full text), tests pass,
documentation updated, remaining limitations documented (see §9).

## 8. Risks & mitigations

| Risk | Mitigation |
|------|-----------|
| Local API has no documented per-item `GET …/fulltext` | Implement `fulltext_item` first, fall back to attachment bytes + PyMuPDF (D9); both branches tested; state which branch ran in the method docstring |
| pyzotero 1.x churned in 2025–2026 (module layout moved to `src/pyzotero`, `dump()` return type changed, exceptions renamed) | Pin `pyzotero>=1.15.2`; touch only the stable read API (`top`, `items`, `collection_items_top`, `children`, `item`, `file`, `fulltext_item`, `everything`); catch the `PyZoteroError` base class, not specific subclasses |
| Local API cannot be tested in CI | Gated `zotero_local` marker + probe → xfail, mirroring the existing service-availability design; mocked tests carry the coverage |
| Optional dep invisible to bioconda users (`pyzotero` is conda-forge only) | Documented in README: conda users add `-c conda-forge pyzotero`; base install unaffected |
| Large libraries make `everything()` slow | Single cached item fetch per instance (D5/`_get_scoped_items`); `collection` parameter narrows scope; `qmode` defaults to the cheap title/creator search |
| `Query` filters silently ignored | Every unsupported filter raises `NotImplementedError` (D8); date filtering documented in the docstring |
| Writing into the user's library by accident | Only Read-API calls are used; no write/upload/delete calls in the module |

## 9. Known limitations to document (not to fix here)

- Zotero is a *bibliography* database: there is no full-text XML, so `Publication.tables` and
  `figure_descriptions` stay empty; figure text is only available via the PDF path (`PymupdfParser`).
- No licence / preprint / open-access filters (issue's `Query` fields are silently meaningless for Zotero).
- Local API: Zotero must be running with the local API enabled; only the logged-in user's library (no groups).
- `api_key` needs "library access" permission; read-only keys are recommended in the docs.
- Group libraries work only against the remote API.

## 10. Explicitly out of scope (candidate follow-up issues)

- Writing/importing into Zotero (`create_items`, `attachment_both`, `authorize_local`) — needs local write
  consent flows.
- Syncing Zotero attachments into `figure_storage` recursively, and sub-collection traversal
  (`all_collections`) when a user wants a collection tree.
- Mapping Zotero **saved searches** to `Query` (both APIs expose them).
- Regenerating the untracked `aoptk_literature.puml` architecture diagrams (not in git today — mention in the
  PR whether the maintainer wants them refreshed).

## 11. Open questions for the user

1. Naming: `Zotero` (matches the `PMC`/`PubMed`/`EuropePMC`/`AOPWiki` style) shadows `pyzotero.Zotero` in
   `from pyzotero import Zotero` — acceptable since our import is function-local? (Plan assumes yes.)
2. Should `full_text_search` default to `True`? `everything` is a heavier server-side query; the plan defaults
   it to `False` (title/creator/year), mirroring the conservative defaults elsewhere.
3. Is the client-side `Query.date` filter (D8) acceptable, or should it raise `NotImplementedError` like the
   other four flags?
