"""Checks on the pinned catalog of LLM models offered by the CERIT-SC endpoint.

`models/llm_models.json` is refreshed by `scripts/update_llm_models.sh`, which a weekly workflow
runs. Everything here is about what the catalog says about *our* configuration, and the flags are
deliberately non-blocking: a model being retired by the provider is not a defect in the code under
test, and failing every open PR over it would only teach people to ignore the suite. The weekly
catalog PR is the channel meant to get a human to act.

That non-blocking property rests on this project not configuring `filterwarnings = error`. Adding
that setting would turn every flag below into a hard failure, which is a decision worth making on
purpose rather than by inheriting a stricter default.
"""

from __future__ import annotations
import json
import warnings
from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Any
import pytest
from aoptk.text_generation_api import DEFAULT_MODEL
from aoptk.text_generation_api import DEFAULT_VISION_MODEL

catalog_path = Path(__file__).resolve().parent.parent / "models" / "llm_models.json"

# Statuses the provider has been observed to report. A name outside this set means the service
# changed its vocabulary, which is worth knowing before `archived` stops meaning what we think.
known_statuses = frozenset({"online", "archived"})

# Past this age the catalog is stale enough that its statements about availability are guesses.
max_catalog_age_days = 14


class ModelCatalogWarning(UserWarning):
    """Something the catalog says about our configuration that a human should look at."""


def flag(condition: bool, message: str) -> None:
    """Report a catalog finding without failing the suite."""
    if condition:
        warnings.warn(message, ModelCatalogWarning, stacklevel=2)


def load_catalog() -> dict[str, Any]:
    """Read the pinned catalog."""
    return json.loads(catalog_path.read_text(encoding="utf-8"))


def models_by_name(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Index the catalog's models by name, case-insensitively."""
    return {model["name"].lower(): model for model in catalog["models"]}


def parse_timestamp(value: str) -> datetime:
    """Parse one of the catalog's timestamps, which the update script always writes as UTC.

    `fromisoformat` understands the `Z` suffix from 3.11, which is this project's floor. A naive
    value is rejected rather than assumed to be local time, so an exchange of the timestamp format
    surfaces as a complaint here instead of as arithmetic that is silently hours out.
    """
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        message = f"catalog timestamp {value!r} carries no timezone"
        raise ValueError(message)
    return parsed.astimezone(UTC)


def test_catalog_is_well_formed():
    """The committed catalog is structurally what the tests and the workflow assume.

    This is the one test here that fails: a malformed catalog makes every other check here vacuous,
    and it means the refresh script or its schema agreement broke.
    """
    catalog = load_catalog()

    assert catalog["schema_version"] == 1
    assert parse_timestamp(catalog["observed_at"]) <= datetime.now(UTC)
    names = [model["name"] for model in catalog["models"]]
    assert names, "the catalog lists no models"
    assert len(names) == len(set(names)), "duplicate model names"
    folded = [name.lower() for name in names]
    # Every lookup here is case-insensitive (the provider writes `Gpt-oss-120b`, the constant is
    # `gpt-oss-120b`), so two names differing only in case would make those lookups ambiguous.
    assert len(folded) == len(set(folded)), "two model names differ only by case"
    assert names == sorted(names, key=str.lower), "models are not sorted case-insensitively"
    for model in catalog["models"]:
        assert {"name", "status", "first_seen", "last_seen", "task_class", "note"} <= set(model)
        parse_timestamp(model["first_seen"])
        parse_timestamp(model["last_seen"])
        assert model["status"], model["name"]


@pytest.mark.parametrize("model_name", [DEFAULT_MODEL, DEFAULT_VISION_MODEL])
def test_default_models_are_known_to_the_catalog(model_name: str):
    """Each default is either listed by the provider, or flagged as unknown to it.

    A default missing from the catalog, or listed as archived, is reported rather than failed: the
    endpoint accepts model names the status page does not list, and only a live call can tell
    "retired" from "not monitored here".
    """
    catalog = load_catalog()
    listed = models_by_name(catalog).get(model_name.lower())

    if listed is None:
        saw = catalog["previous_observed_at"] or "never"
        flag(
            True,
            f"DEFAULT model {model_name!r} is not in {catalog_path.name}; the catalog last saw"
            f" the provider on {saw} and cannot say whether it is available.",
        )
        return

    # The two flags below are mutually exclusive branches over the same value; the status check
    # comes first so that an unexpected word is named as unexpected rather than going unreported.
    flag(
        listed["status"] not in known_statuses,
        f"Model {model_name!r} has unrecognised status {listed['status']!r}; the provider may have"
        " changed its vocabulary and this suite's meaning of `archived` may no longer hold.",
    )
    flag(
        listed["status"] == "archived",
        f"DEFAULT model {model_name!r} is archived by the provider (last seen"
        f" {listed['last_seen'][:10]}). The vision tests xfail rather than fail on a retired model,"
        " so check them explicitly rather than trusting a green suite.",
    )


def test_generative_defaults_are_not_paired_with_a_non_generative_model():
    """The vision default should name a generative model.

    The catalog infers `task_class` from the model name, so this is a heuristic and only a warning.
    It exists because embedding and reranking endpoints accept a chat request and answer with
    something that is not an answer.
    """
    catalogued = models_by_name(load_catalog())
    for model_name in (DEFAULT_MODEL, DEFAULT_VISION_MODEL):
        model = catalogued.get(model_name.lower())
        if model is None:
            continue  # already flagged by test_default_models_are_known_to_the_catalog
        flag(
            "non-generative" in model["task_class"],
            f"DEFAULT model {model_name!r} looks non-generative ({model['task_class']}); aoptk"
            " issues chat completions against it.",
        )


def test_reports_models_the_provider_added_since_the_last_refresh():
    """Flag models that appeared between the catalog's previous refresh and its last one.

    `first_seen` comes from the provider and is preserved across refreshes by the update script, so
    a model first seen after `previous_observed_at` is an addition the catalog has already recorded
    but nobody has looked at. This is the offline half of "a new model is available"; the live half
    is `scripts/update_llm_models.sh --check` exiting 1, which is what the weekly workflow acts on.
    """
    catalog = load_catalog()
    previous = catalog["previous_observed_at"]
    if not previous:
        pytest.skip("the catalog has only ever been observed once, so nothing is new to it")
    previous_at = parse_timestamp(previous)
    added = [model["name"] for model in catalog["models"] if parse_timestamp(model["first_seen"]) > previous_at]
    flag(
        bool(added),
        f"{len(added)} model(s) appeared at the provider since the previous refresh"
        f" ({previous[:10]}): {', '.join(added)}. Consider whether one fits aoptk's needs better"
        " than the current defaults.",
    )


def test_catalog_is_recently_observed():
    """A stale catalog says nothing about what is available now, so say so out loud."""
    observed_at = parse_timestamp(load_catalog()["observed_at"])
    age_days = (datetime.now(UTC) - observed_at).days
    flag(
        age_days > max_catalog_age_days,
        f"{catalog_path.name} was observed {age_days} days ago; run scripts/update_llm_models.sh."
        " Its statements about availability are stale.",
    )


def test_our_defaults_are_recorded_in_the_catalog():
    """The models we depend on name themselves as such, so the catalog explains itself to a reader.

    Unlike the availability flags, this one is a plain assertion: it concerns only files in this
    repository and cannot come true by accident. Matching on the constant's name rather than on the
    word "aoptk" matters, because the default note of every unreviewed model also mentions aoptk.
    """
    catalogued = models_by_name(load_catalog())
    defaults = [(DEFAULT_MODEL, "DEFAULT_MODEL"), (DEFAULT_VISION_MODEL, "DEFAULT_VISION_MODEL")]
    for model_name, constant in defaults:
        model = catalogued.get(model_name.lower())
        if model is None:
            pytest.skip(f"{model_name!r} is not catalogued; nothing to annotate")
        assert constant in model["note"], f"{model_name}: not recorded as the {constant}"
