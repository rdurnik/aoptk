"""Helpers that turn unavailable external services into expected test failures.

Parts of this test suite depend on remote services (NCBI E-utilities, Europe PMC, the CERIT
LLM gateway). Those services are occasionally down, overloaded, or reconfigured, which shows
up either as a connectivity/HTTP failure while probing the endpoint, or as a server-side error
reported by the service itself. Neither case is a defect in aoptk, so such tests are reported
as expected failures (xfailed) instead of failures or errors:

- Before a test runs, the endpoints it needs are probed (once per session, cached). If an
  endpoint does not answer, the test is xfailed via ``require_*_service``.
- If a test fails with an exception that indicates a problem on the service side (5xx status,
  timeouts, blocked/unknown model, ...), the failure is turned into an xfail by the hook in
  ``tests/conftest.py``, which delegates to ``is_environment_or_service_problem_call``.
"""

from __future__ import annotations
import os
import re
import time
from typing import TYPE_CHECKING
from typing import Any
import pytest
import requests

if TYPE_CHECKING:
    from collections.abc import Iterator

# Probes must be fast - a service that does not answer within this budget counts as unavailable.
probe_timeout = 10
# A service that failed a probe is unhealthy; do not repeat the expensive probe for every test.
unhealthy_cache_ttl = 300
# First HTTP status that reports a problem of the service itself rather than of the request.
http_server_error_status = 500

# Exception classes whose presence means the remote service misbehaved. Referenced by name so
# that this module does not have to import the SDKs at collection time. Status errors (the
# openai.*Error and requests.HTTPError family) are classified by their status code instead.
server_problem_exception_names = frozenset(
    {
        "openai.APIConnectionError",
        "openai.APITimeoutError",
        "requests.exceptions.ConnectionError",
        "requests.exceptions.Timeout",
        "http.client.RemoteDisconnected",
        "ConnectionResetError",
        "TimeoutError",
    },
)
# HTTP statuses that are reported by a healthy service about itself, not about the request.
server_problem_status_codes = frozenset({429, 500, 502, 503, 504})
# Substrings that mark a failure as a problem on the service side rather than in aoptk.
server_problem_message_patterns = (
    "temporarily unavailable",
    "timeout waiting for worker",
    "search backend failed",
    "model is blocked",
    "invalid model name",
    "no deployments found",
    "service unavailable",
    "bad gateway",
    "gateway timeout",
    "too many requests",
    "rate limit",
    "overloaded",
    "connection reset by peer",
)
# e.g. "Error code: 503", "Status: 500".
server_problem_status_regex = re.compile(r"(?:error code|status)\D{0,3}5\d\d", re.IGNORECASE)
# Credentials a test environment may legitimately not provide, mapped to the messages their
# SDKs produce when they are missing. Like an outage, they say nothing about aoptk - but only
# while the variable really is unset, so that a broken wiring inside aoptk still fails loudly
# in an environment where the credential is available.
environment_problem_credentials: dict[str, tuple[str, ...]] = {
    "CERIT_API_KEY": ("api_key client option must be set", "openai_api_key environment variable"),
}

# Probe results of the current session: endpoint -> (timestamp, failure detail; empty = healthy).
_probe_cache: dict[str, tuple[float, str]] = {}

# Endpoints needed to query the NCBI PMC database.
pmc_endpoints = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi",
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=liver+cancer&retmax=1",
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pmc&id=12416454",
)
# Endpoints needed to query the NCBI PubMed database.
pubmed_endpoints = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi",
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=liver+cancer&retmax=1",
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=38081985",
)
# Europe PMC mirrors the same articles and shares figure/PDC image URLs with the PMC fixture
# data, so tests using PMC publications need both services.
europepmc_endpoints = (
    "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=liver%20cancer&format=json&pageSize=1",
    "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12231352/fullTextXML",
)
# Text generation endpoint used by TextGenerationAPI.
llm_models_endpoint = os.getenv("AOPKT_LLM_MODELS_URL", "https://llm.ai.e-infra.cz/v1/models")
# PubChem compound identification endpoint used by PubChemAPI.
pubchem_endpoints = ("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/thioacetamide/cids/JSON",)
# AOP-Wiki knowledge base endpoint used by AOPWiki.
aop_wiki_endpoints = ("https://aopwiki.org/aops/38.json",)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]) -> Iterator[Any]:  # noqa: ARG001
    """Report failures caused by a misbehaving external service as expected failures.

    Re-exported from ``tests/conftest.py`` so that pytest picks it up for the whole suite.
    """
    report = yield
    if report is not None and report.failed and is_service_or_environment_problem_call(call):
        assert call.excinfo is not None  # a failure always carries an exception
        report.wasxfail = f"external service problem: {call.excinfo.value}"
        report.outcome = "skipped"
    return report


def require_pmc_service() -> None:
    """Xfail the calling test unless the NCBI PMC service answers."""
    xfail_if_unavailable(*pmc_endpoints)


def require_pubmed_service() -> None:
    """Xfail the calling test unless the NCBI PubMed service answers."""
    xfail_if_unavailable(*pubmed_endpoints)


def require_europepmc_service() -> None:
    """Xfail the calling test unless the Europe PMC service answers."""
    xfail_if_unavailable(*europepmc_endpoints)


def require_pmc_and_europepmc_services() -> None:
    """Xfail the calling test unless both NCBI PMC and Europe PMC answer."""
    xfail_if_unavailable(*pmc_endpoints, *europepmc_endpoints)


def require_llm_service() -> None:
    """Xfail the calling test unless the text generation service answers.

    The API key is deliberately not sent to the probe endpoint: the probe only checks whether
    the service is up, so that tests which do not call it stay runnable without credentials.
    Missing credentials, blocked models and other service-side problems surface during the
    test itself and are turned into xfails by the makereport hook.
    """
    xfail_if_unavailable(llm_models_endpoint)


def require_pubchem_service() -> None:
    """Xfail the calling test unless the PubChem service answers."""
    xfail_if_unavailable(*pubchem_endpoints)


def require_aop_wiki_service() -> None:
    """Xfail the calling test unless the AOP-Wiki service answers."""
    xfail_if_unavailable(*aop_wiki_endpoints)


def xfail_if_unavailable(*endpoints: str) -> None:
    """Xfail the calling test as soon as one of the given endpoints does not answer."""
    for endpoint in endpoints:
        detail = unavailable_reason(endpoint)
        if detail is not None:
            pytest.xfail(f"external service unavailable: {endpoint} ({detail})")


def unavailable_reason(endpoint: str) -> str | None:
    """Return why the endpoint is currently unavailable, or None when it answers successfully."""
    cached = _probe_cache.get(endpoint)
    if cached is not None and (cached[1] == "" or time.monotonic() - cached[0] < unhealthy_cache_ttl):
        return cached[1] or None
    try:
        response = requests.get(endpoint, timeout=probe_timeout)
    except requests.RequestException as error:
        return _remember(endpoint, f"{type(error).__name__}: {error}")
    if response.status_code >= http_server_error_status:
        return _remember(endpoint, f"HTTP {response.status_code}: {response.text[:200]}")
    # 4xx means the service answers and merely rejects our unauthenticated probe.
    _probe_cache[endpoint] = (time.monotonic(), "")
    return None


def _remember(endpoint: str, detail: str) -> str:
    _probe_cache[endpoint] = (time.monotonic(), detail)
    return detail


def is_service_or_environment_problem_call(call: pytest.CallInfo[Any]) -> bool:
    """Return whether a test call failed because of the environment, not because of aoptk."""
    if call.excinfo is None:
        return False
    exception = call.excinfo.value
    if isinstance(exception, (AssertionError, pytest.skip.Exception, pytest.xfail.Exception)):
        return False
    if is_server_problem(exception) or is_environment_problem(exception):
        return True
    # Long-running helpers often wrap the service failure in their own exception, so also
    # look at the rendered traceback for the signatures of a misbehaving service.
    return any(is_server_problem(line) or is_environment_problem(line) for line in _traceback_lines(call))


def is_environment_problem(exception_or_message: BaseException | str) -> bool:
    """Return whether credentials missing from this environment caused the failure."""
    message = (str(exception_or_message) if not isinstance(exception_or_message, str) else exception_or_message).lower()
    return any(
        not os.getenv(variable) and any(pattern in message for pattern in patterns)
        for variable, patterns in environment_problem_credentials.items()
    )


def is_server_problem(exception_or_message: BaseException | str) -> bool:
    """Return whether the exception (or any exception it chains) indicates a service problem."""
    if isinstance(exception_or_message, str):
        return _message_indicates_server_problem(exception_or_message)
    seen: set[int] = set()
    current: BaseException | None = exception_or_message
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if _exception_indicates_server_problem(current) or _message_indicates_server_problem(str(current)):
            return True
        current = current.__cause__ or current.__context__
    return False


def _exception_indicates_server_problem(exception: BaseException) -> bool:
    if f"{type(exception).__module__}.{type(exception).__name__}" in server_problem_exception_names:
        return True
    # Both the OpenAI SDK and requests expose the HTTP status of the failing response.
    status_code = getattr(exception, "status_code", None)
    if not isinstance(status_code, int):
        status_code = getattr(getattr(exception, "response", None), "status_code", None)
    return isinstance(status_code, int) and status_code in server_problem_status_codes


def _message_indicates_server_problem(message: str) -> bool:
    lowered = message.lower()
    return any(pattern in lowered for pattern in server_problem_message_patterns) or bool(
        server_problem_status_regex.search(lowered),
    )


def _traceback_lines(call: pytest.CallInfo[Any]) -> Iterator[str]:
    if call.excinfo is None:
        return iter(())
    try:
        representation = call.excinfo.getrepr(style="long")
    except Exception:  # noqa: BLE001 - a broken traceback must never change the test outcome
        return iter(())
    if representation is None:
        return iter(())
    return iter(str(representation).splitlines())
