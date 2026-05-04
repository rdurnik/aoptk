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