from __future__ import annotations
import pytest
from aoptk.chemical import Chemical
from aoptk.effect import Effect
from aoptk.relationships.find_relationship import FindRelationships
from aoptk.relationships.relationship import Relationship
from aoptk.relationships.zero_shot_classification_single import ZeroShotClassificationSingle


def test_can_create():
    """Test that ZeroShotClassification can be instantiated."""
    actual = ZeroShotClassificationSingle()
    assert actual is not None


def test_implements_interface():
    """Test that ZeroShotClassification implements FindRelationships interface."""
    assert issubclass(ZeroShotClassificationSingle, FindRelationships)


def test_normalize_chemical_not_empty():
    """Test that normalize_chemical method returns a non-empty result."""
    actual = ZeroShotClassificationSingle().find_relationships(text="", chemicals=[], effects=[])
    assert actual is not None


@pytest.mark.parametrize(
    ("text", "chemicals", "effects", "expected_relationships"),
    [
        (
            "Acetaminophen causes liver fibrosis.",
            [Chemical(name="acetaminophen")],
            [Effect(name="liver fibrosis")],
            [
                Relationship(
                    relationship="positive",
                    chemical=Chemical(name="acetaminophen"),
                    effect=Effect(name="liver fibrosis"),
                ),
            ],
        ),
        (
            "Cancer is caused by thioacetamide, not by acetaminophen.",
            [Chemical(name="acetaminophen"), Chemical(name="thioacetamide")],
            [Effect(name="cancer")],
            [
                Relationship(
                    relationship="negative",
                    chemical=Chemical(name="acetaminophen"),
                    effect=Effect(name="cancer"),
                ),
                Relationship(
                    relationship="positive",
                    chemical=Chemical(name="thioacetamide"),
                    effect=Effect(name="cancer"),
                ),
            ],
        ),
        ("Methotrexate induced renal fibrosis.", [Chemical(name="methotrexate")], [Effect(name="liver fibrosis")], []),
        (
            "Esculin did not inhibit thioacetamide-induced hepatic fibrosis and inflammation in mice.",
            [Chemical(name="esculin")],
            [Effect(name="liver fibrosis")],
            [],
        ),
        (
            "Esculin did not inhibit thioacetamide-induced hepatic fibrosis and inflammation in mice.",
            [Chemical(name="thioacetamide")],
            [Effect(name="liver fibrosis")],
            [
                Relationship(
                    relationship="positive",
                    chemical=Chemical(name="thioacetamide"),
                    effect=Effect(name="liver fibrosis"),
                ),
            ],
        ),
        (
            "Just some random text with no effect and no chemical in here.",
            [],
            [],
            [],
        ),
        (
            "Effect of thioacetamide on liver fibrosis was not studied in"
            " this study. We did, however, study the effect of other chemicals.",
            [Chemical(name="thioacetamide")],
            [Effect(name="liver fibrosis")],
            [],
        ),
        (
            "Effect of thioacetamide on liver fibrosis was studied in this study.",
            [Chemical(name="thioacetamide")],
            [Effect(name="liver fibrosis")],
            [],
        ),
        (
            "Thioacetamide was studied in this study.",
            [Chemical(name="thioacetamide")],
            [Effect(name="liver fibrosis")],
            [],
        ),
    ],
)
def test_find_relationships(
    text: str,
    chemicals: list[Chemical],
    effects: list[Effect],
    expected_relationships: list[Relationship],
):
    """Test find_relationships method with multiple chemicals and effects."""
    actual = ZeroShotClassificationSingle(
        model="MoritzLaurer/deberta-v3-large-zeroshot-v2.0",
        threshold=0.8,
    ).find_relationships(text=text, chemicals=chemicals, effects=effects)

    def sort_key(r: Relationship) -> tuple[str, str, str]:
        return (r.relationship, r.chemical.name, r.effect.name)

    assert sorted(actual, key=sort_key) == sorted(expected_relationships, key=sort_key)
