import pytest
from aoptk.cleaning import CleanText
from aoptk.html_tag_remover import HTMLTagRemover


def test_can_create():
    """Test that HTMLTagRemover can be instantiated."""
    actual = HTMLTagRemover()
    assert actual is not None


def test_implements_interface():
    """Test that HTMLTagRemover implements CleanText interface."""
    assert issubclass(HTMLTagRemover, CleanText)


def test_clean_text_data_not_empty():
    """Test that clean_text() method returns non-empty result."""
    actual = HTMLTagRemover().clean_text("")
    assert actual is not None


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
def test_clean_text(text_with_html_tags: str, expected: str):
    """Test that clean_text() method removes HTML tags correctly."""
    actual = HTMLTagRemover().clean_text(text_with_html_tags)
    assert actual == expected
