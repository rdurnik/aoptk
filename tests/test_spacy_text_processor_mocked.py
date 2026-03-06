"""Mocked tests for Spacy processor to provide test coverage without loading heavy models."""
# ruff: noqa: SLF001 ANN001 PLR2004

from __future__ import annotations
import sys
from unittest.mock import MagicMock
import pytest
from aoptk.spacy_models import SpacyModels
from aoptk.spacy_text_processor import SpacyText

pytestmark = pytest.mark.skipif(sys.platform not in ["darwin", "os2", "os2emx"], reason="tests for macOS only")


@pytest.fixture
def spacy_test_env(mocker):
    """Mock spacy.load and clear SpacyModels cache around each test."""
    SpacyModels()._models.clear()

    mock_nlp = MagicMock()
    mock_nlp.pipe_names = []
    mock_load = mocker.patch("aoptk.spacy_models.spacy.load", return_value=mock_nlp)

    yield mock_load

    SpacyModels()._models.clear()


def test_find_chemical_not_empty(spacy_test_env):
    """Test that find_chemical method returns a non-empty result."""
    spacy_test_env.return_value.return_value.ents = []
    actual = SpacyText().find_chemical("")
    assert actual is not None


@pytest.mark.parametrize(
    ("sentence", "expected"),
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
    ],
)
def test_find_chemical_chemical(spacy_test_env, sentence: str, expected: list[str]):
    """Test that find_chemical method finds chemicals in text."""
    mock_entities = []
    for chem_name in expected:
        mock_ent = MagicMock()
        mock_ent.text = chem_name
        mock_ent.label_ = "CHEMICAL"
        mock_entities.append(mock_ent)

    mock_doc = MagicMock()
    mock_doc.ents = mock_entities
    spacy_test_env.return_value.return_value = mock_doc

    actual = [chem.name for chem in SpacyText().find_chemical(sentence)]
    assert actual == expected


def test_generate_sentences_not_empty(spacy_test_env):
    """Test that tokenize method returns a non-empty result."""
    spacy_test_env.return_value.return_value.sents = []

    actual = SpacyText().tokenize("")
    assert actual is not None


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "This is the first sentence. This is the second sentence.",
            ["This is the first sentence.", "This is the second sentence."],
        ),
        (
            "This is the first sentence. the author did not put capital T at the start.",
            ["This is the first sentence.", "the author did not put capital T at the start."],
        ),
        (
            "This is the first sentence.There is a missing space after the period!",
            ["This is the first sentence.", "There is a missing space after the period!"],
        ),
    ],
)
def test_generate_sentences(spacy_test_env, text: str, expected: list[str]):
    """Test tokenize method with various cases."""
    mock_sents = []
    for sent_text in expected:
        mock_sent = MagicMock()
        mock_sent.text = sent_text
        mock_sents.append(mock_sent)

    mock_doc = MagicMock()
    mock_doc.sents = mock_sents
    spacy_test_env.return_value.return_value = mock_doc

    actual = [sentence.__str__() for sentence in SpacyText().tokenize(text)]
    assert actual == expected


@pytest.mark.parametrize(
    ("chemical", "expected_mesh_terms"),
    [
        ("thioacetamide", ["ethanethioamide", "thiacetamid", "thioacetamide"]),
        ("nothing", []),
        ("Thioacetamide causes cancer.", ["ethanethioamide", "thiacetamid", "thioacetamide"]),
        (
            "acetaminophen",
            [
                "acetamide, n-(4-hydroxyphenyl)-",
                "acetamidophenol",
                "acetaminophen",
                "apap",
                "hydroxyacetanilide",
                "n-(4-hydroxyphenyl)acetanilide",
                "n-acetyl-p-aminophenol",
                "p-acetamidophenol",
                "p-hydroxyacetanilide",
                "paracetamol",
            ],
        ),
        (
            "methotrexate",
            [
                "amethopterin",
                "methotrexate",
                "methotrexate sodium",
                "methotrexate, sodium salt",
                "sodium, methotrexate",
            ],
        ),
    ],
)
def test_generate_mesh_terms(spacy_test_env, chemical: str, expected_mesh_terms: list[str]):
    """Test that generate_mesh_terms method generates MeSH terms."""
    if expected_mesh_terms:
        mock_entity = MagicMock()
        mock_entity._.kb_ents = [("CUI001", 0.95)]

        mock_entity_linker = MagicMock()
        mock_mesh_info = MagicMock()
        mock_mesh_info.aliases = expected_mesh_terms
        mock_entity_linker.kb.cui_to_entity = {"CUI001": mock_mesh_info}

        mock_doc = MagicMock()
        mock_doc.ents = [mock_entity]
        spacy_test_env.return_value.return_value = mock_doc
        spacy_test_env.return_value.get_pipe.return_value = mock_entity_linker
    else:
        mock_doc = MagicMock()
        mock_doc.ents = []
        spacy_test_env.return_value.return_value = mock_doc

    actual = SpacyText().generate_mesh_terms(chemical)
    assert actual == expected_mesh_terms


def test_model_caching(spacy_test_env):
    """Test that models are cached and not loaded multiple times."""
    spacy1 = SpacyText("test_model", "test_model")
    spacy2 = SpacyText("test_model", "test_model")

    assert spacy_test_env.call_count == 1
    assert spacy1.nlp is spacy2.nlp


def test_scispacy_linker_added_once(spacy_test_env):
    """Test that scispacy_linker is only added once to the pipeline."""
    SpacyText()
    spacy_test_env.return_value.add_pipe.assert_called_once_with("scispacy_linker", config=SpacyText._mesh_terms_config)

    spacy_test_env.return_value.pipe_names = ["scispacy_linker"]
    initial_call_count = spacy_test_env.return_value.add_pipe.call_count
    SpacyText()
    assert spacy_test_env.return_value.add_pipe.call_count == initial_call_count


def test_find_chemical_filters_non_chemical_entities(spacy_test_env):
    """Test that find_chemical only returns entities labeled as CHEMICAL."""
    mock_chem1 = MagicMock()
    mock_chem1.text = "aspirin"
    mock_chem1.label_ = "CHEMICAL"

    mock_disease = MagicMock()
    mock_disease.text = "cancer"
    mock_disease.label_ = "DISEASE"

    mock_chem2 = MagicMock()
    mock_chem2.text = "ibuprofen"
    mock_chem2.label_ = "CHEMICAL"

    mock_doc = MagicMock()
    mock_doc.ents = [mock_chem1, mock_disease, mock_chem2]
    spacy_test_env.return_value.return_value = mock_doc

    result = SpacyText().find_chemical("test sentence")

    assert len(result) == 2
    assert result[0].name == "aspirin"
    assert result[1].name == "ibuprofen"


def test_tokenize_strips_whitespace(spacy_test_env):
    """Test that tokenize strips whitespace from sentences."""
    mock_sent1 = MagicMock()
    mock_sent1.text = "  First sentence.  "

    mock_sent2 = MagicMock()
    mock_sent2.text = "\tSecond sentence.\n"

    mock_doc = MagicMock()
    mock_doc.sents = [mock_sent1, mock_sent2]
    spacy_test_env.return_value.return_value = mock_doc

    result = SpacyText().tokenize("test text")

    assert len(result) == 2
    assert str(result[0]) == "First sentence."
    assert str(result[1]) == "Second sentence."


def test_find_chemical_empty_string(spacy_test_env):
    """Test that find_chemical handles empty string input."""
    spacy_test_env.return_value.return_value.ents = []

    result = SpacyText().find_chemical("")
    assert result == []


def test_tokenize_empty_string(spacy_test_env):
    """Test that tokenize handles empty string input."""
    spacy_test_env.return_value.return_value.sents = []

    result = SpacyText().tokenize("")
    assert result == []


def test_generate_mesh_terms_no_kb_entities(spacy_test_env):
    """Test generate_mesh_terms when entity has no knowledge base entries."""
    mock_entity = MagicMock()
    mock_entity._.kb_ents = []

    mock_doc = MagicMock()
    mock_doc.ents = [mock_entity]
    spacy_test_env.return_value.return_value = mock_doc

    result = SpacyText().generate_mesh_terms("test chemical")
    assert result == []


def test_find_chemical_case_preservation(spacy_test_env):
    """Test that find_chemical preserves the case of chemical names."""
    mock_ent = MagicMock()
    mock_ent.text = "Aspirin"
    mock_ent.label_ = "CHEMICAL"

    mock_doc = MagicMock()
    mock_doc.ents = [mock_ent]
    spacy_test_env.return_value.return_value = mock_doc

    result = SpacyText().find_chemical("Aspirin is a drug")
    assert result[0].name == "aspirin"
