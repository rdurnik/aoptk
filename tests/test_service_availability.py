"""Tests for the service availability helpers themselves."""

from __future__ import annotations
import subprocess
import sys
import time
from typing import TYPE_CHECKING
import pytest
from tests.service_availability import _probe_cache
from tests.service_availability import is_server_problem
from tests.service_availability import unavailable_reason
from tests.service_availability import unhealthy_cache_ttl
from tests.service_availability import xfail_if_unavailable

if TYPE_CHECKING:
    from pathlib import Path


# Messages observed in failing CI runs of this repository.
ncbi_search_backend_message = (
    "Search Backend failed: An error occurred while processing request. Status: 500. "
    "Source: /api/search/?r= Details: Search is temporarily unavailable. "
    "Please try again later. Details: Timeout waiting for worker."
)
blocked_model_message = "Error code: 403 - {'error': {'message': 'litellm.PermissionDeniedError: Model is blocked'}}"
invalid_model_message = (
    "Error code: 400 - {'error': {'message': '/chat/completions: Invalid model name passed in model=redhatai-scout.'}}"
)


@pytest.fixture(autouse=True)
def clear_probe_cache():
    """Make sure probes are not shared between tests."""
    _probe_cache.clear()
    yield
    _probe_cache.clear()


class _FakeStatusError(Exception):
    """Stand-in for exceptions carrying an HTTP status, like the OpenAI SDK errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@pytest.mark.parametrize(
    ("exception", "expected"),
    [
        (RuntimeError(ncbi_search_backend_message), True),
        (ConnectionResetError("Connection reset by peer"), True),
        (_FakeStatusError(blocked_model_message, status_code=403), True),
        (_FakeStatusError(invalid_model_message, status_code=400), True),
        (_FakeStatusError("HTTP 503 on lookup", status_code=503), True),
        (_FakeStatusError("HTTP 404 on lookup", status_code=404), False),
        (AssertionError("expected 10101 to be 9999"), False),
        (ValueError("some logic error"), False),
    ],
)
def test_is_server_problem(exception: BaseException, expected: bool):
    """Server-side problems are distinguished from genuine test failures."""
    assert is_server_problem(exception) is expected


def test_is_server_problem_checks_chained_exceptions():
    """A service problem wrapped into another exception is still recognized."""
    wrapped = TimeoutError("batch failed")
    wrapped.__cause__ = RuntimeError(ncbi_search_backend_message)
    assert is_server_problem(wrapped) is True


def test_unavailable_reason_for_unreachable_endpoint():
    """An endpoint that refuses connections is reported as unavailable."""
    detail = unavailable_reason("http://127.0.0.1:9/nothing-here")
    assert detail is not None
    assert "ConnectionError" in detail


def test_unavailable_reason_is_cached():
    """A recent verdict for a failing endpoint is reused instead of re-probing."""
    endpoint = "http://127.0.0.1:9/nothing-here"
    assert unavailable_reason(endpoint) is not None
    probe_count = len(_probe_cache)
    _probe_cache[endpoint] = (time.monotonic(), "cached failure")
    assert unavailable_reason(endpoint) == "cached failure"
    assert len(_probe_cache) == probe_count


def test_stale_failure_is_probed_again():
    """An endpoint that failed longer ago than the TTL gets a second chance."""
    endpoint = "http://127.0.0.1:9/nothing-here"
    _probe_cache[endpoint] = (time.monotonic() - unhealthy_cache_ttl - 1, "cached failure")
    detail = unavailable_reason(endpoint)
    assert detail is not None
    assert detail != "cached failure"


def test_xfail_if_unavailable_xfails():
    """An unreachable endpoint turns the calling test into an expected failure."""

    def calling_test() -> None:
        xfail_if_unavailable("http://127.0.0.1:9/nothing-here")

    with pytest.raises(pytest.xfail.Exception) as excinfo:
        calling_test()
    assert "external service unavailable" in str(excinfo.value)


def test_xfail_if_unavailable_passes_for_available_endpoint():
    """A reachable endpoint leaves the test running."""
    xfail_if_unavailable("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi")


def test_failures_of_unavailable_services_are_reported_as_xfailed(tmp_path: Path):
    """End-to-end: a test failing due to a service problem is reported as xfailed, not failed."""
    test_file = tmp_path / "test_simulated_outage.py"
    test_file.write_text(
        f"""
import http.client
from urllib.error import HTTPError
import pytest
from tests.service_availability import xfail_if_unavailable


def test_endpoint_down():
    xfail_if_unavailable("http://127.0.0.1:9/nothing-here")


def test_service_reports_internal_problem():
    raise RuntimeError(
        "Search Backend failed: An error occurred while processing request. Status: 500. "
        "Details: Search is temporarily unavailable. Please try again later."
    )


def test_disconnected_service():
    raise http.client.RemoteDisconnected("Remote end closed connection without response")


@pytest.mark.xfail(raises=HTTPError)
def test_service_problem_below_existing_xfail_mark():
    # Mirrors tests/test_pmc.py::test_get_id_large_query: NCBI reports a 500 through
    # Bio.Entrez as RuntimeError, which the existing xfail(raises=HTTPError) does not cover.
    raise RuntimeError("{ncbi_search_backend_message}")


def test_genuine_failure_still_fails():
    assert 1 == 2

@pytest.mark.xfail(raises=HTTPError)
def test_genuine_wrong_exception_below_xfail_mark_still_fails():
    # An unexpected exception below an existing xfail(raises=...) mark must stay a failure.
    assert 1 == 2
""",
        encoding="utf-8",
    )
    completed = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "pytest", "-p", "tests.service_availability", "-q", str(test_file)],
        capture_output=True,
        text=True,
        check=False,
    )
    summary = next(line for line in completed.stdout.splitlines() if "passed" in line or "failed" in line)
    assert "4 xfailed" in summary
    assert "2 failed" in summary
