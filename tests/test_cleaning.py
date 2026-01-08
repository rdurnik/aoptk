import pytest
from aoptk.cleaning.html_tag_remover import HTMLTagRemover
from aoptk.cleaning.text_cleaner import CleaningPipeline
from aoptk.cleaning.text_cleaner import TextCleaner


def test_can_create():
    """Test that HTMLTagRemover can be instantiated."""
    actual = HTMLTagRemover()
    assert actual is not None


def test_implements_interface():
    """Test that HTMLTagRemover implements CleanText interface."""
    assert issubclass(HTMLTagRemover, TextCleaner)


def test_clean_text_data_not_empty():
    """Test that clean_text() method returns non-empty result."""
    actual = HTMLTagRemover().clean("")
    assert actual is not None


@pytest.mark.parametrize("cleaner", [HTMLTagRemover(), CleaningPipeline([HTMLTagRemover()])])
@pytest.mark.parametrize(
    ("text_with_html_tags", "expected"),
    [
        (
            "<h4>Introduction</h4>Liver fibrosis was the topic of this study.",
            "IntroductionLiver fibrosis was the topic of this study.",
        ),
        (
            "<h4>Background</h4> Thioacetamide was used in the experiment.",
            "Background Thioacetamide was used in the experiment.",
        ),
        (
            "<title>Abstract</title> <p><bold>Background: "
            "</bold>Liver fibrosis is a major global public health issue.</p>",
            "Abstract Background: Liver fibrosis is a major global public health issue.",
        ),
    ],
)
def test_clean_text(cleaner: TextCleaner, text_with_html_tags: str, expected: str):
    """Test that clean_text() method removes HTML tags correctly."""
    actual = cleaner.clean(text_with_html_tags)
    assert actual == expected
