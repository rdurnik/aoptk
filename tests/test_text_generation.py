from __future__ import annotations
import pytest
from aoptk.abbreviations.abbreviation_translator import AbbreviationTranslator
from aoptk.chemical import Chemical
from aoptk.effect import Effect
from aoptk.find_chemical import FindChemical
from aoptk.relationship_type import Causative
from aoptk.relationship_type import Inhibitive
from aoptk.relationship_type import RelationshipType
from aoptk.relationships.find_relationship import FindRelationships
from aoptk.relationships.relationship import Relationship
from aoptk.text_generation_api import TextGenerationAPI


def sort_key(r: Relationship) -> tuple[str, str, str]:
    """Sort key for Relationship objects.

    Args:
        r (Relationship): Relationship object.
    """
    return (r.relationship_type, r.chemical.name, r.effect.name)


def test_can_create():
    """Can create ScispacyFindChemical instance."""
    actual = TextGenerationAPI()
    assert actual is not None


def test_implements_interface_find_chemical():
    """ScispacyFindChemical implements FindChemical interface."""
    assert isinstance(TextGenerationAPI(), FindChemical)
    assert isinstance(TextGenerationAPI(), FindRelationships)
    assert isinstance(TextGenerationAPI(), AbbreviationTranslator)


def test_find_chemical_not_empty():
    """Test that find_chemical method returns a non-empty result."""
    actual = TextGenerationAPI().find_chemical("")
    assert actual is not None


def test_find_relationships_not_empty():
    """Test that find_relationships method returns a non-empty result."""
    actual = TextGenerationAPI().find_relationships("", relationship_type=None, chemicals=[], effects=[])
    assert actual is not None


def test_translate_abbreviation_not_empty():
    """Test that translate_abbreviation method returns a non-empty result."""
    actual = TextGenerationAPI().translate_abbreviation("")
    assert actual is not None


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Thioacetamide was studied for its effect on liver cells.", ["thioacetamide"]),
        ("HepaRG cells were used as an experimental model.", []),
        (
            "Thioacetamide, carbon tetrachloride and ethanol were used to induce liver injury.",
            ["thioacetamide", "carbon tetrachloride", "ethanol"],
        ),
        ("Thioacetamide causes cancer.", ["thioacetamide"]),
        ("CCl4 and thioacetamide were tested for hepatotoxicity.", ["ccl4", "thioacetamide"]),
        ("Liver fibrosis and cancer were studied.", []),
        ("Thioacetamide (TAA) was used to induce liver fibrosis.", ["thioacetamide"]),
        ("Mice were subjected to carbon tetrachloride-induced liver fibrosis.", ["carbon tetrachloride"]),
        ("Fibrosis was suppressed by treatment with N-acetyl-L-cysteine", ["n-acetyl-l-cysteine"]),
        (
            " Here, we demonstrate the utility of bioprinted tissue constructs comprising primary "
            "hepatocytes, hepatic stellate cells, and endothelial cells to model methotrexate- and "
            "thioacetamide-induced liver injury leading to fibrosis.",
            ["methotrexate", "thioacetamide"],
        ),
        (
            "Female mice (C57Blc) were induced by 4 injections of peritoneal carbon-tetrachloride within 10 days",
            ["carbon tetrachloride"],
        ),
    ],
)
def test_find_chemical_chemical(text: str, expected: list[str]):
    """Test that find_chemical method finds chemicals in text."""
    actual = [chem.name for chem in TextGenerationAPI().find_chemical(text)]
    assert actual == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("TAA was studied for its effect on liver cells.", "Thioacetamide was studied for its effect on liver cells."),
        (
            "The liver MTs were exposed to a known profibrotic chemical, thioacetamide (TAA) and three representative "
            "environmental chemicals (TCDD, benzo[a]pyrene (BaP) and PCB126).",
            "The liver MTs were exposed to a known profibrotic chemical, thioacetamide and three representative "
            "environmental chemicals (2,3,7,8-tetrachlorodibenzo-p-dioxin, "
            "benzo[a]pyrene and 3,3',4,4',5-pentachlorobiphenyl).",
        ),
    ],
)
def test_translate_abbreviations(text: str, expected: list[str]):
    """Test that find_chemical method finds chemicals in text."""
    actual = TextGenerationAPI().translate_abbreviation(text)
    assert actual == expected


@pytest.mark.parametrize(
    ("text", "relationship_type", "chemicals", "effects", "expected_relationships"),
    [
        (
            "Acetaminophen causes liver fibrosis.",
            Causative(),
            [Chemical(name="acetaminophen")],
            [Effect(name="liver fibrosis")],
            [
                Relationship(
                    relationship_type=Causative().positive,
                    chemical=Chemical(name="acetaminophen"),
                    effect=Effect(name="liver fibrosis"),
                    context="Acetaminophen causes liver fibrosis.",
                ),
            ],
        ),
        (
            "Cancer is caused by thioacetamide, not by acetaminophen.",
            Causative(),
            [Chemical(name="acetaminophen"), Chemical(name="thioacetamide")],
            [Effect(name="cancer")],
            [
                Relationship(
                    relationship_type=Causative().negative,
                    chemical=Chemical(name="acetaminophen"),
                    effect=Effect(name="cancer"),
                    context="Cancer is caused by thioacetamide, not by acetaminophen.",
                ),
                Relationship(
                    relationship_type=Causative().positive,
                    chemical=Chemical(name="thioacetamide"),
                    effect=Effect(name="cancer"),
                    context="Cancer is caused by thioacetamide, not by acetaminophen.",
                ),
            ],
        ),
        (
            "Methotrexate induced renal fibrosis.",
            Causative(),
            [Chemical(name="methotrexate")],
            [Effect(name="liver fibrosis")],
            [],
        ),
        (
            "Esculin did not inhibit thioacetamide-induced hepatic fibrosis and inflammation in mice.",
            Causative(),
            [Chemical(name="esculin")],
            [Effect(name="liver fibrosis")],
            [],
        ),
        (
            "Esculin did not inhibit thioacetamide-induced hepatic fibrosis and inflammation in mice.",
            Causative(),
            [Chemical(name="thioacetamide")],
            [Effect(name="liver fibrosis")],
            [
                Relationship(
                    relationship_type=Causative().positive,
                    chemical=Chemical(name="thioacetamide"),
                    effect=Effect(name="liver fibrosis"),
                    context="Esculin did not inhibit thioacetamide-induced hepatic fibrosis and inflammation in mice.",
                ),
            ],
        ),
        (
            "Just some random text with no effect and no chemical in here.",
            Causative(),
            [],
            [],
            [],
        ),
        (
            "Effect of thioacetamide on liver fibrosis was not studied in"
            " this study. We did, however, study the effect of other chemicals.",
            Causative(),
            [Chemical(name="thioacetamide")],
            [Effect(name="liver fibrosis")],
            [],
        ),
        (
            "Effect of thioacetamide on liver fibrosis was studied in this study.",
            Causative(),
            [Chemical(name="thioacetamide")],
            [Effect(name="liver fibrosis")],
            [],
        ),
        (
            "Thioacetamide was studied in this study.",
            Causative(),
            [Chemical(name="thioacetamide")],
            [Effect(name="liver fibrosis")],
            [],
        ),
    ],
)
def test_find_relationships(
    text: str,
    relationship_type: RelationshipType,
    chemicals: list[Chemical],
    effects: list[Effect],
    expected_relationships: list[Relationship],
):
    """Test find_relationships method with multiple chemicals and effects."""
    actual = TextGenerationAPI().find_relationships(
        text=text, relationship_type=relationship_type, chemicals=chemicals, effects=effects
    )

    assert sorted(actual, key=sort_key) == sorted(expected_relationships, key=sort_key)


def test_relationship_images():
    """Test find_relationships_in_image method with an image."""
    actual = TextGenerationAPI(model="mistral-large").find_relationships_in_image(
        image_path="tests/test_figures/gjic.jpeg",
        relationship_type=Inhibitive(),
        effects=[Effect(name="gap junction intercellular communication")],
        context="gjic.jpeg",
    )
    assert any(
        r.chemical.name == "dibutyl phthalate"
        and r.effect.name == "gap junction intercellular communication"
        and r.relationship_type == Inhibitive().positive
        for r in actual
    )
