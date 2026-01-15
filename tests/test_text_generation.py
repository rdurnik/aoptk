from aoptk.text_generation_api import TextGenerationAPI
from aoptk.find_chemical import FindChemical
from aoptk.relationships.find_relationship import FindRelationships
from aoptk.abbreviations.abbreviation_translator import AbbreviationTranslator
from aoptk.chemical import Chemical
from aoptk.effect import Effect
from aoptk.relationships.relationship import Relationship
import pytest

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
    actual = TextGenerationAPI().find_relationships("", chemicals=[], effects=[])
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
        ("Thioacetamide (TAA) was used to induce liver fibrosis.", ["thioacetamide", "taa"]),
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
            ["carbon-tetrachloride"],
        ),
        (
            "Transforming growth factor-alpha secreted from ethanol-exposed hepatocytes"
            " contributes to development of alcoholic hepatic fibrosis.",
            ["ethanol"],
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
        ("The liver MTs were exposed to a known profibrotic chemical, thioacetamide (TAA) and three representative environmental chemicals (TCDD, benzo[a]pyrene (BaP) and PCB126).", 
         "The liver MTs were exposed to a known profibrotic chemical, thioacetamide and three representative environmental chemicals (2,3,7,8‑tetrachlorodibenzo‑p‑dioxin, benzo[a]pyrene and 3,3′,4,4′,5‑pentachlorobiphenyl)."),
    ],
)
def test_translate_abbreviations(text: str, expected: list[str]):
    """Test that find_chemical method finds chemicals in text."""
    actual = TextGenerationAPI().translate_abbreviation(text)
    assert actual == expected

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
    actual = TextGenerationAPI().find_relationships(text=text, chemicals=chemicals, effects=effects)

    def sort_key(r: Relationship) -> tuple[str, str, str]:
        return (r.relationship, r.chemical.name, r.effect.name)

    assert sorted(actual, key=sort_key) == sorted(expected_relationships, key=sort_key)