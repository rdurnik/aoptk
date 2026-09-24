# ruff: noqa: PLR2004
# ruff: noqa: SLF001
from collections.abc import Iterator
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from pytest_mock import MockerFixture
from aoptk.chemical import Chemical
from aoptk.text_generation_api import LLMFailureError
from aoptk.text_generation_api import TextGenerationAPI

CHEMICAL_TEXT = "Paracetamol is toxic to the liver."
# A bulleted answer only counts as invalid once it carries a newline, because the patterns are
# matched against the answer after stripping - a bullet at the very start is stripped away.
BULLETED_RESPONSE = "- thioacetamide\n- methotrexate"
TWO_CHEMICALS_RESPONSE = "thioacetamide ; methotrexate"
TRICHLORFON = Chemical(name="trichlorfon")
CHEMICAL_LIST = [Chemical(name="thioacetamide")]


@pytest.fixture(autouse=True)
def no_backoff(monkeypatch: pytest.MonkeyPatch) -> None:
    """Drop the retry backoff so tests that exhaust the attempt budget stay fast."""
    monkeypatch.setattr(TextGenerationAPI, "prompt_backoff_multiplier", 0.0)


def completion(content: str | None) -> SimpleNamespace:
    """Build the minimal stand-in for a completion, holding just what the code reads."""
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


def endless(*contents: str | None) -> Iterator[SimpleNamespace]:
    """Yield one completion per content, then repeat the last one forever.

    Repeating rather than raising keeps tests that assert on the attempt budget honest: a
    surplus call returns an answer instead of blowing up with StopIteration.
    """
    answers = [completion(content) for content in contents]
    yield from answers
    while answers:
        yield answers[-1]


def mocked_api(mocker: MockerFixture, *contents: str | None) -> tuple[TextGenerationAPI, Mock]:
    """Build an API whose completion endpoint answers with `contents`, one per call.

    Only the endpoint facing the service is mocked, so the empty-answer and validator logic
    the retry layer reacts to is the real one. The dummy key keeps these tests independent of
    `CERIT_API_KEY`: nothing here reaches the service, so they must not be skipped without it.

    Returns:
        tuple[TextGenerationAPI, Mock]: The API, and the mock counting completion calls.
    """
    api = TextGenerationAPI(api_key="mock-api-key")
    create = mocker.patch.object(api.client.chat.completions, "create", side_effect=endless(*contents))
    return api, create


def test_prompt_retries_empty_answer_and_returns_the_first_usable_one(mocker: MockerFixture):
    """Two answers the transport accepted but left empty are re-requested, the third is used."""
    api, create = mocked_api(mocker, None, "", "PCB-123")

    assert api._prompt("some prompt") == "PCB-123"
    assert create.call_count == 3


def test_prompt_raises_llm_failure_once_the_attempt_budget_is_exhausted(mocker: MockerFixture):
    """An answer that stays empty fails loudly instead of collapsing into an empty result."""
    api, create = mocked_api(mocker, "")

    with pytest.raises(LLMFailureError):
        api._prompt("some prompt")
    assert create.call_count == TextGenerationAPI.prompt_attempts


def test_extraction_fails_loudly_when_an_attempt_is_empty_after_an_invalid_one(mocker: MockerFixture):
    """A rejected answer is not passed off as an answer once a later attempt comes back empty."""
    api, create = mocked_api(mocker, BULLETED_RESPONSE, None)

    with pytest.raises(LLMFailureError):
        api.find_chemicals(CHEMICAL_TEXT)
    assert create.call_count == TextGenerationAPI.prompt_attempts


def test_find_chemicals_retries_invalid_answer_and_keeps_the_valid_one(mocker: MockerFixture):
    """A bulleted answer is re-requested, and the semicolon separated one is parsed."""
    api, create = mocked_api(mocker, BULLETED_RESPONSE, TWO_CHEMICALS_RESPONSE)

    result = api.find_chemicals(CHEMICAL_TEXT)

    assert [chem.name for chem in result] == ["thioacetamide", "methotrexate"]
    assert create.call_count == 2


def test_find_chemicals_returns_no_chemicals_when_every_answer_is_invalid(mocker: MockerFixture):
    """The documented empty-list contract holds even when every attempt is rejected."""
    api, create = mocked_api(mocker, BULLETED_RESPONSE)

    assert api.find_chemicals(CHEMICAL_TEXT) == []
    assert create.call_count == TextGenerationAPI.prompt_attempts


def test_normalization_retries_invalid_answer_and_keeps_the_valid_one(mocker: MockerFixture):
    """An answer naming two chemicals is re-requested, the single name is used."""
    api, create = mocked_api(mocker, TWO_CHEMICALS_RESPONSE, "thioacetamide")

    matched = api._find_matching_name(TRICHLORFON, CHEMICAL_LIST)

    assert matched is not None
    assert matched.name == "thioacetamide"
    assert create.call_count == 2


def test_normalization_keeps_the_original_name_when_every_answer_is_invalid(mocker: MockerFixture):
    """The documented fallback holds even when every attempt is rejected."""
    api, create = mocked_api(mocker, TWO_CHEMICALS_RESPONSE)

    assert api._find_matching_name(TRICHLORFON, CHEMICAL_LIST) == TRICHLORFON
    assert create.call_count == TextGenerationAPI.prompt_attempts
