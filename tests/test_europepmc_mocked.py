from __future__ import annotations
import pytest
from requests import HTTPError
from requests import Response
from aoptk.literature.databases.europepmc import EuropePMC


class MockResponse(Response):
    """Mock response object for simulating requests responses."""

    def __init__(self, status_code: int, json_data: dict | None = None):
        super().__init__()
        self.status_code = status_code
        self._json_data = json_data

    def json(self) -> dict | None:
        """Return the JSON data for the response."""
        return self._json_data


@pytest.fixture
def mock_http_error(monkeypatch: pytest.MonkeyPatch):
    """Fixture for mocking HTTP error response."""

    def mock_get(*_args: tuple, **_kwargs: dict) -> MockResponse:
        """Simulate a non-OK response from EuropePMC."""
        return MockResponse(status_code=500)

    monkeypatch.setattr("requests.Session.get", mock_get)


@pytest.fixture
def mock_success_response(monkeypatch: pytest.MonkeyPatch):
    """Fixture for mocking successful response."""

    def mock_get(*_args: tuple, **_kwargs: dict) -> MockResponse:
        """Simulate a successful response with valid abstract data from EuropePMC."""
        return MockResponse(
            status_code=200,
            json_data={
                "resultList": {
                    "result": [{"abstractText": "Test abstract text", "title": "Test Title", "pmid": "12345678"}],
                },
            },
        )

    monkeypatch.setattr("requests.Session.get", mock_get)


@pytest.mark.usefixtures("mock_http_error")
def test_generate_abstract_for_given_id_http_error(provide_temp_storage: dict, provide_temp_storage_figures: dict):
    """Test that HTTPError is raised when EuropePMC returns non-OK response."""
    with pytest.raises(HTTPError):
        EuropePMC(
            "12345678",
            storage=provide_temp_storage,
            figure_storage=provide_temp_storage_figures,
        ).get_abstracts()[0]


@pytest.mark.usefixtures("mock_success_response")
def test_generate_abstract_for_given_id_success(provide_temp_storage: dict, provide_temp_storage_figures: dict):
    """Test successful abstract retrieval with mocked response."""
    result = EuropePMC(
        "12345678",
        storage=provide_temp_storage,
        figure_storage=provide_temp_storage_figures,
    ).get_abstracts()[0]
    assert result.text == "Test abstract text"
