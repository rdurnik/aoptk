# `aoptk` developer documentation

If you're looking for user documentation, go [here](README.md).

## Development install

```shell
# (from the project root directory)
# install runtime + development dependencies from the lockfile
uv sync --frozen --extra dev

# install documentation dependencies only
uv sync --frozen --extra docs
```

Use `uv run` to execute tools in the managed environment.

## Running the tests

There are two ways to run tests.

The first way uses the uv-managed environment:

```shell
uv run pytest -v
```

The second is to use `tox`, which can be run via `uvx`, i.e. not necessarily inside the uv-managed environment, but then builds the necessary virtual environments itself by simply running:

```shell
uvx tox
```

Testing with `tox` allows for keeping the testing environment separate from your development environment.
The development environment will typically accumulate (old) packages during development that interfere with testing; this problem is avoided by testing with `tox`.

### Tests that need an external service

Most tests run offline. Some talk to a service that aoptk does not control - NCBI, Europe PMC, the LLM gateway, AOP-Wiki, PubChem, or Zotero - and those are dealt with by `tests/service_availability.py`: if the service is down, the test is reported as an expected failure rather than a failure, because it says nothing about aoptk.

Tests that need credentials simply skip when the environment does not provide them. For Zotero:

```shell
# needs ZOTERO_LIBRARY_ID and ZOTERO_API_KEY of a library you may read
uv run pytest tests/test_zotero.py -v

# additionally needs the Zotero desktop app running with its local API enabled
# (Settings -> Advanced), and reads the library the app is signed in to
AOPKT_TEST_ZOTERO_LOCAL=1 uv run pytest tests/test_zotero.py -v
```

The local-API tests carry the `zotero_local` marker, which CI deselects so that no job depends on a desktop app on the runner:

```shell
uv run pytest -m "not openai and not zotero_local" -v
```

Without `AOPKT_TEST_ZOTERO_LOCAL=1` they skip anyway; the marker keeps them out of the run entirely.

Everything the Zotero backend does is covered offline by `tests/test_zotero_mocked.py`, which drives a fixture library and runs with or without `pyzotero` installed. To exercise the real import path, sync with the extra: `uv sync --frozen --extra dev --extra zotero`.

### Test coverage

In addition to just running the tests to see if they pass, they can be used for coverage statistics, i.e. to determine how much of the package's code is actually executed during tests.
Inside the package directory, run:

```shell
uv run coverage run
```

This runs tests and stores the result in a `.coverage` file.
To see the results on the command line, run

```shell
uv run coverage report
```

`coverage` can also generate output in HTML and other formats; see `uv run coverage help` for more information.

## Running linters locally

For linting and sorting imports we will use [ruff](https://beta.ruff.rs/docs/).

```shell
# linter
uv run ruff check .

# linter with automatic fixing
uv run ruff check . --fix
```

To fix readability of your code style you can use [yapf](https://github.com/google/yapf).

## Generating the API docs

```shell
uv run make -C docs html
```

The documentation will be in `docs/_build/html`

If you do not have `make` use

```shell
uv run sphinx-build -b html docs docs/_build/html
```

To find undocumented Python objects run

```shell
uv run make -C docs coverage
cat docs/_build/coverage/python.txt
```

To [test snippets](https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html) in documentation run

```shell
uv run make -C docs doctest
```

## Versioning

Bumping the version across all files is done with [bump-my-version](https://github.com/callowayproject/bump-my-version), e.g.

```shell
bump-my-version bump major  # bumps from e.g. 0.3.2 to 1.0.0
bump-my-version bump minor  # bumps from e.g. 0.3.2 to 0.4.0
bump-my-version bump patch  # bumps from e.g. 0.3.2 to 0.3.3
```

## Making a release

This section describes how to make a release in 3 parts:

1. preparation
1. making a release on PyPI
1. making a release on GitHub

### (1/3) Preparation


1. Verify that the information in [`CITATION.cff`](CITATION.cff) is correct using `uv run cffconvert --validate`
1. Make sure the [version has been updated](#versioning).
1. Run the unit tests with `uv run pytest -v`

### (2/3) PyPI

Follow the documentation outlined [here](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/) to setup the trusted publishing workflow with PyPI.

### (3/3) GitHub

Don't forget to also make a [release on GitHub](https://github.com/rdurnik/aoptk/releases/new).GitHub-Zenodo integration will also trigger Zenodo into making a snapshot of your repository and sticking a DOI on it.