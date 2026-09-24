from __future__ import annotations
from aoptk.relationships import relationship_type
from aoptk.relationships.relationship_type import Activation
from aoptk.relationships.relationship_type import Alleviation
from aoptk.relationships.relationship_type import Causation
from aoptk.relationships.relationship_type import Induction
from aoptk.relationships.relationship_type import Inhibition
from aoptk.relationships.relationship_type import Mitigation
from aoptk.relationships.relationship_type import Prevention
from aoptk.relationships.relationship_type import Promotion
from aoptk.relationships.relationship_type import Regulation
from aoptk.relationships.relationship_type import RelationshipType
from aoptk.text_generation_api import other_topics_labels
from aoptk.text_generation_api import topics


def all_relationship_types() -> list[RelationshipType]:
    """Return one instance of every concrete relationship type."""
    return [
        Inhibition(),
        Causation(),
        Activation(),
        Promotion(),
        Prevention(),
        Induction(),
        Alleviation(),
        Mitigation(),
        Regulation(),
    ]


def test_relationship_type_is_instance():
    """Each concrete relationship type is a RelationshipType with all fields set."""
    for rel_type in all_relationship_types():
        assert isinstance(rel_type, RelationshipType)
        assert rel_type.positive
        assert rel_type.positive_verb
        assert rel_type.negative
        assert rel_type.negative_verb
        assert rel_type.definition


def test_positive_labels_are_distinct_and_lowercase():
    """Positive labels must be unique single lowercase words (used verbatim in prompts)."""
    positives = [rel_type.positive for rel_type in all_relationship_types()]
    assert len(positives) == len(set(positives))
    for positive in positives:
        assert positive.islower()
        assert " " not in positive


def test_positive_and_negative_verb_pairings():
    """Each type pairs its positive verb with the expected positive label."""
    expected = {
        Inhibition(): ("inhibits", "inhibition"),
        Causation(): ("causes", "causation"),
        Activation(): ("activates", "activation"),
        Promotion(): ("promotes", "promotion"),
        Prevention(): ("prevents", "prevention"),
        Induction(): ("induces", "induction"),
        Alleviation(): ("alleviates", "alleviation"),
        Mitigation(): ("mitigates", "mitigation"),
        Regulation(): ("upregulates", "upregulation"),
    }
    for rel_type, (verb, positive) in expected.items():
        assert rel_type.positive_verb == verb
        assert rel_type.positive == positive


def test_regulation_is_directional():
    """Regulation reports direction instead of negation: upregulation vs. downregulation."""
    regulation = Regulation()
    assert regulation.positive == "upregulation"
    assert regulation.positive_verb == "upregulates"
    assert regulation.negative == "downregulation"
    assert regulation.negative_verb == "downregulates"


def test_equivalence_is_by_positive_label():
    """Two instances of the same type compare equal and share a hash (needed for set.difference)."""
    assert Inhibition() == Inhibition()
    assert hash(Inhibition()) == hash(Inhibition())
    assert Inhibition() != Causation()
    assert Inhibition() != "inhibition"


def test_repr():
    """Repr shows the class and positive label."""
    assert repr(Inhibition()) == "Inhibition(positive='inhibition')"


def test_topics_contains_all_relationship_types():
    """The topics set used to exclude other topics in prompts covers every relationship type."""
    for rel_type in all_relationship_types():
        assert rel_type in topics


def test_other_topics_excludes_only_current_type():
    """other_topics_labels drops exactly the current type and keeps all others, even for a fresh instance."""
    for rel_type in all_relationship_types():
        labels = other_topics_labels(rel_type).split(", ")
        assert len(labels) == len(topics) - 1
        assert rel_type.positive not in labels
        expected = {topic.positive for topic in all_relationship_types()} - {rel_type.positive}
        assert set(labels) == expected


def test_other_topics_order_is_stable():
    """Labels are rendered in alphabetical order so prompts are identical across processes."""
    for rel_type in all_relationship_types():
        labels = other_topics_labels(rel_type)
        assert labels == ", ".join(sorted(labels.split(", ")))
        # independent calls with equivalent instances produce identical output
        assert labels == other_topics_labels(type(rel_type)())


def test_definitions_delineate_overlapping_concepts():
    """Definitions of easily-confused pairs explicitly steer away from each other."""
    by_type = {rel_type.positive: rel_type.definition for rel_type in all_relationship_types()}
    # inhibition vs. prevention vs. alleviation vs. mitigation
    assert "prevention" in by_type["inhibition"]
    assert "alleviation" in by_type["inhibition"]
    assert "inhibition" in by_type["prevention"]
    assert "alleviation" in by_type["prevention"]
    assert "prevention" in by_type["alleviation"]
    assert "inhibition" in by_type["alleviation"]
    assert "mitigation" in by_type["alleviation"]
    assert "prevention" in by_type["mitigation"]
    # causation vs. promotion vs. activation vs. induction
    assert "promotion" in by_type["causation"]
    assert "induction" in by_type["causation"]
    assert "causation" in by_type["promotion"]
    assert "activation" in by_type["promotion"]
    assert "promotion" in by_type["activation"]
    assert "causation" in by_type["activation"]
    assert "causation" in by_type["induction"]
    # regulation (positive label: upregulation) vs. induction vs. inhibition
    assert "downregulation" in by_type["upregulation"]
    assert "induction" in by_type["upregulation"]
    assert "inhibition" in by_type["upregulation"]
    assert "regulation" in by_type["induction"]


def test_old_class_names_removed():
    """Renamed/merged classes must not be importable anymore."""
    assert not hasattr(relationship_type, "Causative")
    assert not hasattr(relationship_type, "Inhibitive")
    assert not hasattr(relationship_type, "Upregulation")
    assert not hasattr(relationship_type, "Downregulation")


def test_prompt_fields_render():
    """Jinja-style attribute access used by the prompt templates resolves for every type."""
    for rel_type in all_relationship_types():
        prompt_line = f"{rel_type.positive_verb} {rel_type.positive} {rel_type.negative}"
        assert len(prompt_line) > 0
