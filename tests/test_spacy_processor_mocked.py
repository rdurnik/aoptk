"""Mocked tests for Spacy processor to provide test coverage without loading heavy models."""
# ruff: noqa: SLF001 ANN001 PLR2004

from __future__ import annotations
from unittest.mock import MagicMock
from unittest.mock import patch
import pytest
from aoptk.find_chemical import FindChemical
from aoptk.sentence_generator import SentenceGenerator
from aoptk.spacy_processor import Spacy


@patch("aoptk.spacy_processor.spacy.load")
def test_can_create(mock_spacy_load):
    """Can create Spacy instance."""
    # Mock the spacy.load to return a mock NLP object
    mock_nlp = MagicMock()
    mock_nlp.pipe_names = []
    mock_spacy_load.return_value = mock_nlp

    actual = Spacy()
    assert actual is not None


@patch("aoptk.spacy_processor.spacy.load")
def test_implements_interface_find_chemical(mock_spacy_load):
    """Spacy implements FindChemical interface."""
    mock_nlp = MagicMock()
    mock_nlp.pipe_names = []
    mock_spacy_load.return_value = mock_nlp

    assert isinstance(Spacy(), FindChemical)


@patch("aoptk.spacy_processor.spacy.load")
def test_find_chemical_not_empty(mock_spacy_load):
    """Test that find_chemical method returns a non-empty result."""
    mock_nlp = MagicMock()
    mock_nlp.pipe_names = []
    mock_doc = MagicMock()
    mock_doc.ents = []
    mock_nlp.return_value = mock_doc
    mock_spacy_load.return_value = mock_nlp

    actual = Spacy().find_chemical("")
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
@patch("aoptk.spacy_processor.spacy.load")
def test_find_chemical_chemical(mock_spacy_load, sentence: str, expected: list[str]):
    """Test that find_chemical method finds chemicals in text."""
    # Clear model cache
    Spacy._models.clear()

    # Create mock entities based on expected chemicals
    mock_entities = []
    for chem_name in expected:
        mock_ent = MagicMock()
        mock_ent.text = chem_name
        mock_ent.label_ = "CHEMICAL"
        mock_entities.append(mock_ent)

    # Setup mock NLP
    mock_nlp = MagicMock()
    mock_nlp.pipe_names = []
    mock_doc = MagicMock()
    mock_doc.ents = mock_entities
    mock_nlp.return_value = mock_doc
    mock_spacy_load.return_value = mock_nlp

    actual = [chem.name for chem in Spacy().find_chemical(sentence)]
    assert actual == expected


@patch("aoptk.spacy_processor.spacy.load")
def test_implements_interface_sentence_generator(mock_spacy_load):
    """Test that Spacy implements SentenceGenerator interface."""
    mock_nlp = MagicMock()
    mock_nlp.pipe_names = []
    mock_spacy_load.return_value = mock_nlp

    assert issubclass(Spacy, SentenceGenerator)


@patch("aoptk.spacy_processor.spacy.load")
def test_generate_sentences_not_empty(mock_spacy_load):
    """Test that tokenize method returns a non-empty result."""
    mock_nlp = MagicMock()
    mock_nlp.pipe_names = []
    mock_doc = MagicMock()
    mock_doc.sents = []
    mock_nlp.return_value = mock_doc
    mock_spacy_load.return_value = mock_nlp

    actual = Spacy().tokenize("")
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
@patch("aoptk.spacy_processor.spacy.load")
def test_generate_sentences(mock_spacy_load, text: str, expected: list[str]):
    """Test tokenize method with various cases."""
    # Clear model cache
    Spacy._models.clear()

    # Create mock sentence objects
    mock_sents = []
    for sent_text in expected:
        mock_sent = MagicMock()
        mock_sent.text = sent_text
        mock_sents.append(mock_sent)

    # Setup mock NLP
    mock_nlp = MagicMock()
    mock_nlp.pipe_names = []
    mock_doc = MagicMock()
    mock_doc.sents = mock_sents
    mock_nlp.return_value = mock_doc
    mock_spacy_load.return_value = mock_nlp

    actual = [sentence.__str__() for sentence in Spacy().tokenize(text)]
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
@patch("aoptk.spacy_processor.spacy.load")
def test_generate_mesh_terms(mock_spacy_load, chemical: str, expected_mesh_terms: list[str]):
    """Test that generate_mesh_terms method generates MeSH terms."""
    # Clear model cache
    Spacy._models.clear()

    # Setup single mock model (default behavior uses same model for both)
    mock_nlp = MagicMock()
    mock_nlp.pipe_names = []
    mock_spacy_load.return_value = mock_nlp

    # If we expect mesh terms, setup entity linking mocks
    if expected_mesh_terms:
        # Create mock entity
        mock_entity = MagicMock()
        mock_entity._.kb_ents = [("CUI001", 0.95)]

        # Create mock entity linker
        mock_entity_linker = MagicMock()
        mock_mesh_info = MagicMock()
        mock_mesh_info.aliases = expected_mesh_terms
        mock_entity_linker.kb.cui_to_entity = {"CUI001": mock_mesh_info}

        # Setup the mesh model
        mock_doc = MagicMock()
        mock_doc.ents = [mock_entity]
        mock_nlp.return_value = mock_doc
        mock_nlp.get_pipe.return_value = mock_entity_linker
    else:
        # No entities found
        mock_doc = MagicMock()
        mock_doc.ents = []
        mock_nlp.return_value = mock_doc

    actual = Spacy().generate_mesh_terms(chemical)
    assert actual == expected_mesh_terms


@patch("aoptk.spacy_processor.spacy.load")
def test_model_caching(mock_spacy_load):
    """Test that models are cached and not loaded multiple times."""
    mock_nlp = MagicMock()
    mock_nlp.pipe_names = []
    mock_spacy_load.return_value = mock_nlp

    # Clear the cache first
    Spacy._models.clear()

    # Create two instances with same model
    spacy1 = Spacy("test_model", "test_model")
    spacy2 = Spacy("test_model", "test_model")

    # spacy.load should only be called once due to caching
    assert mock_spacy_load.call_count == 1

    # Both instances should share the same model
    assert spacy1.nlp is spacy2.nlp


@patch("aoptk.spacy_processor.spacy.load")
def test_scispacy_linker_added_once(mock_spacy_load):
    """Test that scispacy_linker is only added once to the pipeline."""
    # Clear the cache
    Spacy._models.clear()

    mock_nlp = MagicMock()
    mock_nlp.pipe_names = []  # Initially no linker
    mock_spacy_load.return_value = mock_nlp

    # Create first instance - should add linker
    Spacy()
    mock_nlp.add_pipe.assert_called_once_with("scispacy_linker", config=Spacy._mesh_terms_config)

    # Now simulate linker is in pipeline
    mock_nlp.pipe_names = ["scispacy_linker"]

    # Create second instance - should NOT add linker again (model is cached)
    initial_call_count = mock_nlp.add_pipe.call_count
    Spacy()
    # Call count should be the same because model is cached and linker already exists
    assert mock_nlp.add_pipe.call_count == initial_call_count


@patch("aoptk.spacy_processor.spacy.load")
def test_find_chemical_filters_non_chemical_entities(mock_spacy_load):
    """Test that find_chemical only returns entities labeled as CHEMICAL."""
    # Clear model cache
    Spacy._models.clear()

    # Create mixed entities - some CHEMICAL, some not
    mock_chem1 = MagicMock()
    mock_chem1.text = "aspirin"
    mock_chem1.label_ = "CHEMICAL"

    mock_disease = MagicMock()
    mock_disease.text = "cancer"
    mock_disease.label_ = "DISEASE"

    mock_chem2 = MagicMock()
    mock_chem2.text = "ibuprofen"
    mock_chem2.label_ = "CHEMICAL"

    # Setup mock NLP
    mock_nlp = MagicMock()
    mock_nlp.pipe_names = []
    mock_doc = MagicMock()
    mock_doc.ents = [mock_chem1, mock_disease, mock_chem2]
    mock_nlp.return_value = mock_doc
    mock_spacy_load.return_value = mock_nlp

    result = Spacy().find_chemical("test sentence")

    # Should only get the CHEMICAL entities
    assert len(result) == 2
    assert result[0].name == "aspirin"
    assert result[1].name == "ibuprofen"


@patch("aoptk.spacy_processor.spacy.load")
def test_tokenize_strips_whitespace(mock_spacy_load):
    """Test that tokenize strips whitespace from sentences."""
    # Clear model cache
    Spacy._models.clear()

    # Create mock sentences with extra whitespace
    mock_sent1 = MagicMock()
    mock_sent1.text = "  First sentence.  "

    mock_sent2 = MagicMock()
    mock_sent2.text = "\tSecond sentence.\n"

    # Setup mock NLP
    mock_nlp = MagicMock()
    mock_nlp.pipe_names = []
    mock_doc = MagicMock()
    mock_doc.sents = [mock_sent1, mock_sent2]
    mock_nlp.return_value = mock_doc
    mock_spacy_load.return_value = mock_nlp

    result = Spacy().tokenize("test text")

    # Whitespace should be stripped
    assert len(result) == 2
    assert str(result[0]) == "First sentence."
    assert str(result[1]) == "Second sentence."
