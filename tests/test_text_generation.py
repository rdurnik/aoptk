from __future__ import annotations
import os
from pathlib import Path
import pandas as pd
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

pytestmark = pytest.mark.skipif(
    os.getenv("GITHUB_ACTIONS") == "true",
    reason="Skip in Github Actions to save energy consumption (large model download required).",
)


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
    actual = TextGenerationAPI().find_relationships_in_text("", relationship_type=None, chemicals=[], effects=[])
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
            "environmental chemicals (TCDD and PCB126).",
            "The liver MTs were exposed to a known profibrotic chemical, thioacetamide and three representative "
            "environmental chemicals (2,3,7,8-tetrachlorodibenzo-p-dioxin "
            "and 3,3',4,4',5-pentachlorobiphenyl).",
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
    actual = TextGenerationAPI().find_relationships_in_text(
        text=text,
        relationship_type=relationship_type,
        chemicals=chemicals,
        effects=effects,
    )

    assert sorted(actual, key=sort_key) == sorted(expected_relationships, key=sort_key)


def test_relationship_images():
    """Test find_relationships_in_image method with an image."""
    actual = TextGenerationAPI(model="mistral-large").find_relationships_in_image(
        image_path="tests/test_figures/gjic.jpeg",
        relationship_type=Inhibitive(),
        effects=[Effect(name="gap junction intercellular communication")],
    )
    assert any(
        r.chemical.name == "dibutyl phthalate"
        and r.effect.name == "gap junction intercellular communication"
        and r.relationship_type == Inhibitive().positive
        and r.context == "gjic"
        for r in actual
    )


@pytest.fixture
def phthalate_table_data():
    """Provide a sample phthalate table payload for tests."""
    return {
        "Carbon Chain Length.": [
            "Short",
            "Short",
            "Short",
            "Medium",
            "Short",
            "Short",
            "Short",
            "Medium",
            "Medium",
            "Medium",
            "Medium",
            "Medium",
            "Medium",
            "Long",
            "Long",
            "Long",
            "Long",
            "Long",
            "Long",
            "Long",
        ],
        "GJIC.EC 50 b ( µ M) 80": [
            "> 200",
            "> 200",
            "> 200",
            "> 200",
            "70",
            "86",
            "100",
            "13",
            "17",
            "21",
            "16",
            "22",
            "39",
            "58",
            "44",
            "> 200",
            "> 200",
            "> 200",
            "> 200",
            "> 200",
        ],
        "GJIC.µ M ET 50 c (min)": [
            "> 1440",
            "> 1440",
            "> 1440",
            "> 1440",
            "> 1440",
            "> 1440",
            "> 1440",
            "2",
            "10",
            "2",
            "10",
            "10",
            "10",
            "25",
            "17",
            "207",
            "292",
            "711",
            "> 1440",
            "> 1440",
        ],
        "Group.": ["A", "A", "A", "A", "B", "B", "B", "C", "C", "C", "C", "C", "C", "D", "D", "E", "E", "E", "F", "F"],
        "Log Kow a.": [
            "9 GLYPH<2> 10 GLYPH<0> 1 to 1.50",
            "1.46 to 1.90",
            "2.21 to 3",
            "2.37 to 3.07",
            "3.14 to 3.87",
            "2.61 to 3.48",
            "2.92 to 3.36",
            "4.39 to 4.83",
            "3.81 to 4.46",
            "3.57 to 4.91",
            "5.19 to 5.89",
            "4.79 to 6.20",
            "2.82 to 4.61",
            "5.65-6.82",
            "7.4",
            "5.11-8.35",
            "7.84 to 9.08",
            "8.57 to 11.2",
            "9.05",
            "10.36",
        ],
        "MAPK-Erk1 / 2 Activation.FOC d (0.5 h)": [
            "0",
            "0",
            "0",
            "0",
            "5",
            "8",
            "5",
            "24",
            "32",
            "21",
            "32",
            "28",
            "7",
            "4",
            "4",
            "3",
            "3",
            "5",
            "4",
            "4",
        ],
        "MW a g / mol.": [
            "180",
            "194",
            "222",
            "222",
            "250",
            "250",
            "246",
            "278",
            "278",
            "312",
            "306",
            "330",
            "318",
            "363",
            "363",
            "391",
            "391",
            "419",
            "447",
            "447",
        ],
        "Phthalate.": [
            "MMP Monomethyl phthalate",
            "DMP Dimethyl phthalate",
            "DEP Diethyl phthalate",
            "MBP Monobutyl phthalate",
            "DPrP Dipropyl phthalate",
            "DIPrP Diisopropyl phthalate",
            "DAP Diallyl phthalate",
            "DBP Dibutyl phthalate",
            "DIBP Diisibutyl phthalate",
            "BBP Benzyl butyl phthalate",
            "DPeP Dipentyl phthalate",
            "DCHP Dicyclohexyl phthalate",
            "DPhP Diphenyl phthalate",
            "DHpP Diheptyl phthalate",
            "DIHpP Diisoheptyl phthalate",
            "DEHP Di-(2-ethylhexyl) phthalate",
            "DOP Dioctyl phthalate",
            "DINP Diisononyl phthalate",
            "DDP Didecyl phthalate",
            "DIDP Diisodecyl phthalate",
        ],
    }


def test_relationship_table(phthalate_table_data: dict):
    """Test find_relationships_in_table method with a table."""
    actual = TextGenerationAPI().find_relationships_in_table(
        table_df=pd.DataFrame(phthalate_table_data),
        relationship_type=Inhibitive(),
        effects=[Effect(name="gap junction intercellular communication")],
    )
    assert any(
        r.chemical.name == "dibutyl phthalate"
        and r.effect.name == "gap junction intercellular communication"
        and r.relationship_type == Inhibitive().positive
        and r.context == "table"
        for r in actual
    )


@pytest.mark.parametrize(
    ("chemical", "list_of_chemicals", "expected_heading"),
    [
        (
            Chemical(name="paracetamol"),
            [Chemical(name="acetaminophen"), Chemical(name="thioacetamide")],
            "acetaminophen",
        ),
        (Chemical(name="paracetamol"), [Chemical(name="paracetamol"), Chemical(name="thioacetamide")], "paracetamol"),
        (Chemical(name="paracetamol"), [Chemical(name="methotrexate"), Chemical(name="thioacetamide")], None),
        (
            Chemical(name="paracetamol"),
            [Chemical(name="acetaminophen"), Chemical(name="APAP"), Chemical(name="paracetamol")],
            "paracetamol",
        ),
        (
            Chemical(name="paracetamol"),
            [Chemical(name="acetaminophen"), Chemical(name="APAP"), Chemical(name="acetaco")],
            "acetaminophen",
        ),
    ],
)
def test_normalize_chemical(chemical: str, list_of_chemicals: list[str], expected_heading: str):
    """Test that find_chemical method finds chemicals in text."""
    actual = TextGenerationAPI().normalize_chemical(chemical, list_of_chemicals)
    assert actual.heading == expected_heading


def test_extract_text_from_pdf_image():
    """Test that extract_text_from_pdf_image method extracts text from a PDF image."""
    base64_str = (Path("tests/test-data/test_pdf_base64_image.txt").read_text()).strip()
    actual = TextGenerationAPI(model="mistral-large").extract_text_from_pdf_image(base64_str, mime_type="image/jpeg")
    assert ("Polycyclic aromatic hydrocarbons (PAHs), many of which are") in actual


@pytest.mark.parametrize(
    ("text", "images", "expected_chemicals"),
    [
        (
            "Gap junction intracellular communication was studied in this study.",
            ["tests/test_figures/gjic.jpeg"],
            ["dibutyl phthalate"],
        ),
        (
            "Gap junction intracellular communication was not studied in this study.",
            ["tests/test_figures/gjic.jpeg"],
            [],
        ),
        (
            "Thioacetamide leads to the inhibition of gap junction intercellular communication.",
            ["tests/test_figures/gjic.jpeg"],
            ["thioacetamide", "dibutyl phthalate"],
        ),
    ],
)
def test_find_relationships_in_text_and_images(text: str, images: list[str], expected_chemicals: list[str]):
    """Test that find_relationships_in_text_and_images method finds relationships in text and images."""
    actual = TextGenerationAPI(model="mistral-large").find_relationships_in_text_and_images(
        text=text,
        image_paths=images,
        relationship_type=Inhibitive(),
        effects=[Effect(name="gap junction intercellular communication")],
    )

    if not expected_chemicals:
        assert len(actual) == 0
    else:
        for expected_chemical in expected_chemicals:
            assert any(
                r.chemical.name == expected_chemical
                and r.effect.name == "gap junction intercellular communication"
                and r.relationship_type == Inhibitive().positive
                for r in actual
            )
