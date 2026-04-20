import pytest
from aoptk.generate_slides import GenerateSlides
from aoptk.sentence import Sentence
from aoptk.slide_generator import SlideGenerator


def test_can_create():
    """Test that GenerateSlides can be instantiated."""
    actual = GenerateSlides()
    assert actual is not None


def test_implements_interface():
    """Test that GenerateSlides implements SlideGenerator interface."""
    assert issubclass(GenerateSlides, SlideGenerator)


def test_generate_slides_data_not_empty():
    """Test that generate_slides() method returns non-empty result."""
    actual = GenerateSlides().generate_slides([])
    assert actual is not None


@pytest.mark.parametrize(
    ("sentences", "number_of_sentences", "expected"),
    [
        (
            [
                Sentence("This is sentence 1."),
                Sentence("This is sentence 2."),
                Sentence("This is sentence 3."),
                Sentence("This is sentence 4."),
            ],
            3,
            [
                "This is sentence 1. This is sentence 2. This is sentence 3.",
                "This is sentence 2. This is sentence 3. This is sentence 4.",
            ],
        ),
        ([Sentence("This is sentence 1.")], 3, ["This is sentence 1."]),
        ([], 3, [""]),
        (
            [
                Sentence("This is sentence 1."),
                Sentence("This is sentence 2."),
                Sentence("This is sentence 3."),
                Sentence("This is sentence 4."),
            ],
            2,
            [
                "This is sentence 1. This is sentence 2.",
                "This is sentence 2. This is sentence 3.",
                "This is sentence 3. This is sentence 4.",
            ],
        ),
    ],
)
def test_generate_slides(sentences: list[Sentence], number_of_sentences: int, expected: list[str]):
    """Test that generate_slides() method returns expected result."""
    actual = GenerateSlides().generate_slides(sentences, number_of_sentences)
    assert [slide.text for slide in actual] == expected
