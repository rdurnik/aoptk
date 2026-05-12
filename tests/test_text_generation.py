from __future__ import annotations
from pathlib import Path
import pandas as pd
import pytest
from flaky import flaky
from aoptk.chemical import Chemical
from aoptk.effect import Effect
from aoptk.find_chemical import FindChemical
from aoptk.literature.convert_image import ConvertImage
from aoptk.literature.convert_pdf_scan import ConvertPDFScan
from aoptk.literature.find_relevant_publication import FindRelevantPublication
from aoptk.normalization.normalize_chemical import NormalizeChemical
from aoptk.relationships.relationship_type import Causative
from aoptk.relationships.relationship_type import Inhibitive
from aoptk.relationships.relationship_type import RelationshipType
from aoptk.relationships.find_relationship import FindRelationship
from aoptk.relationships.relationship import Relationship
from aoptk.text_generation_api import TextGenerationAPI


def sort_key(r: Relationship) -> tuple[str, str, str]:
    """Sort key for Relationship objects.

    Args:
        r (Relationship): Relationship object.
    """
    return (r.relationship_type, r.chemical.name, r.effect.name)


@pytest.mark.openai
def test_can_create():
    """Can create ScispacyFindChemical instance."""
    actual = TextGenerationAPI()
    assert actual is not None


@pytest.mark.openai
def test_implements_interface_find_chemical():
    """ScispacyFindChemical implements FindChemical interface."""
    assert isinstance(TextGenerationAPI(), FindChemical)
    assert isinstance(TextGenerationAPI(), FindRelationship)
    assert isinstance(TextGenerationAPI(), NormalizeChemical)
    assert isinstance(TextGenerationAPI(), ConvertPDFScan)
    assert isinstance(TextGenerationAPI(), ConvertImage)
    assert isinstance(TextGenerationAPI(), FindRelevantPublication)


@pytest.mark.openai
def test_find_chemical_not_empty():
    """Test that find_chemical method returns a non-empty result."""
    actual = TextGenerationAPI().find_chemicals("")
    assert actual is not None


@pytest.mark.openai
def test_find_relationships_not_empty():
    """Test that find_relationships method returns a non-empty result."""
    actual = TextGenerationAPI().find_relationships_in_text("", relationship_type=None, chemicals=[], effects=[])
    assert actual is not None


@pytest.mark.openai
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "Thioacetamide and ethanol were used to induce liver injury.",
            ["thioacetamide", "ethanol"],
        ),
        (
            "Thioacetamide was used to induce liver injury.",
            ["thioacetamide"],
        ),
        (
            "No chemical was studied here.",
            [],
        ),
    ],
)
def test_find_chemical(text: str, expected: list[str]):
    """Test that find_chemical method finds chemicals in text."""
    actual = [chem.name for chem in TextGenerationAPI().find_chemicals(text)]
    assert actual == expected


@pytest.mark.openai
@pytest.mark.parametrize(
    ("text", "relationship_type", "chemicals", "effects", "expected_relationships"),
    [
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
            "Just some random text with no effect and no chemical in here.",
            Causative(),
            [],
            [],
            [],
        ),
        (
            "Thioacetamide was studied. Acetaminophen caused liver fibrosis.",
            Causative(),
            [Chemical(name="thioacetamide"), Chemical(name="acetaminophen")],
            [Effect(name="liver fibrosis")],
            [
                Relationship(
                    relationship_type=Causative().positive,
                    chemical=Chemical(name="acetaminophen"),
                    effect=Effect(name="liver fibrosis"),
                    context="Thioacetamide was studied. Acetaminophen caused liver fibrosis.",
                ),
            ],
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


@pytest.mark.openai
@flaky
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


@pytest.mark.openai
@pytest.mark.parametrize(
    ("chemical", "list_of_chemicals", "expected_heading"),
    [
        (
            Chemical(name="paracetamol"),
            [Chemical(name="acetaminophen"), Chemical(name="thioacetamide")],
            "acetaminophen",
        ),
    ],
)
def test_normalize_chemical(chemical: Chemical, list_of_chemicals: list[Chemical], expected_heading: str):
    """Test that find_chemical method finds chemicals in text."""
    actual = TextGenerationAPI().normalize_chemical(chemical, list_of_chemicals)
    assert actual.heading == expected_heading


@pytest.mark.openai
def test_extract_text_from_pdf_image():
    """Test that extract_text_from_pdf_image method extracts text from a PDF image."""
    base64_str = (Path("tests/test-data/test_pdf_base64_image.txt").read_text()).strip()
    actual = TextGenerationAPI(model="llama-4-scout-17b-16e-instruct").convert_pdf_scan(
        base64_str,
        mime_type="image/jpeg",
    )
    assert ("Polycyclic aromatic hydrocarbons (PAHs), many of which are") in actual


@pytest.mark.openai
@pytest.mark.parametrize(
    ("text", "images", "expected_chemicals"),
    [
        (
            "Gap junction intracellular communication was studied in this study.",
            ["tests/test_figures/gjic.jpeg"],
            ["dibutyl phthalate"],
        ),
    ],
)
def test_find_relationships_in_text_and_images(text: str, images: list[str], expected_chemicals: list[str]):
    """Test that find_relationships_in_text_and_images method finds relationships in text and images."""
    actual = TextGenerationAPI(model="qwen3.5").find_relationships_in_text_and_images(
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


@pytest.mark.openai
def test_convert_image_to_text():
    """Test that convert_image_to_text method converts an image to text."""
    actual = TextGenerationAPI(model="llama-4-scout-17b-16e-instruct").convert_image(
        "tests/test_figures/gjic.jpeg",
        text="These images are about gap junction intercellular communication.",
    )
    assert "gjic" in actual.lower()


@pytest.mark.openai
@pytest.mark.parametrize(
    ("question", "text", "expected"),
    [
        (
            "Does this publication contain data about drug carriers in HepG2 cells?",
            "Bile acid-based drug carriers were studied here. "
            "Both HepG2 and HepaRG spheroids were used as an experimental model.",
            True,
        ),
        (
            "Does this publication contain data about drug carriers in HeLa cells?",
            "Bile acid-based drug carriers were studied here. "
            "Both HepG2 and HepaRG spheroids were used as an experimental model.",
            False,
        ),
    ],
)
def test_find_relevant_publications(question: str, text: str, expected: bool):
    """Test that find_relevant_publications method finds relevant publications."""
    actual = TextGenerationAPI().find_relevant_publications(question=question, text=text)
    assert actual == expected
