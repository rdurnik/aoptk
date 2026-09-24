from pathlib import Path
import pytest
from aoptk.text_generation_api import DEFAULT_MODEL
from aoptk.text_generation_api import DEFAULT_VISION_MODEL
from aoptk.text_generation_api import TextGenerationAPI

# Models the e-infra endpoint has retired. Naming one again is not a style problem: the endpoint
# answers a retired model with a bad-request error that the test suite classifies as an
# unavailable service, so the affected tests xfail instead of failing.
retired_models = ("llama-4-scout-17b-16e-instruct", "redhatai-scout")

package_dir = Path(__file__).resolve().parent.parent / "src" / "aoptk"


@pytest.mark.parametrize("retired_model", retired_models)
def test_retired_model_is_not_referenced_by_the_library(retired_model: str):
    """No library module asks for a model the endpoint has retired.

    A retired name in `src` cannot be caught by the test suite, because a retired model makes the
    live tests xfail rather than fail. This checks what those tests structurally cannot.
    """
    offenders = sorted(
        str(path.relative_to(package_dir)) for path in package_dir.rglob("*.py") if retired_model in path.read_text()
    )
    assert offenders == []


def test_constructor_default_is_the_shared_constant():
    """The default a caller gets is the documented constant, not a second copy of its value."""
    assert TextGenerationAPI(api_key="mock-api-key").model == DEFAULT_MODEL


def test_model_constants_are_usable():
    """The constants name a model rather than being left empty or placeholder-shaped."""
    for name, model in (("DEFAULT_MODEL", DEFAULT_MODEL), ("DEFAULT_VISION_MODEL", DEFAULT_VISION_MODEL)):
        assert model, name
        assert model == model.strip(), name
        assert " " not in model, name
