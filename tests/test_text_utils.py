import pytest
from aoptk.text_utils import contains_any
from aoptk.text_utils import ends
from aoptk.text_utils import endswith_digit


@pytest.mark.parametrize(
    ("text", "output"),
    [
        (
            "This is a complete sentence.",
            True,
        ),
        (
            "Is this a question?",
            True,
        ),
        (
            "What an exclamation!",
            True,
        ),
        (
            "This sentence has no terminator",
            False,
        ),
        (
            "Sentence with trailing spaces.   ",
            True,
        ),
        (
            "A sentence but there is a reference at the end. [12]",
            True,
        ),
        (
            "A sentence but there is a reference at the end 12,13.",
            True,
        ),
    ],
)
def test_ends_with_sentence_terminator(text: str, output: bool):
    """Test identifying text ending with sentence terminators."""
    assert ends(text) == output


@pytest.mark.parametrize(
    ("text", "output"),
    [
        (
            "Published in 2024",
            True,
        ),
        (
            "Published in 2024.",
            False,
        ),
        (
            "A sentence but there is a reference at the end. 12,13",
            True,
        ),
    ],
)
def test_endswith_digit(text: str, output: bool):
    """Test identifying text ending with sentence terminators."""
    actual = endswith_digit(text)
    assert actual == output


@pytest.mark.parametrize(
    ("text", "patterns", "output"),
    [
        (
            "GLYPH<c=20,font=/HTQHQB+TimesNewRomanPS-ItalicMT"
            ">GLYPH<c=20,font=/HTQHQB+TimesNewRomanPS-ItalicMT"
            ">GLYPH<c=19,font=/HTQHQB+TimesNewRomanPS-ItalicMT"
            ">GLYPH<c=25,font=/HTQHQB+TimesNewRomanPS-ItalicMT"
            ">GLYPH<c=26,font=/HTQHQB+TimesNewRomanPS-ItalicMT"
            ">GLYPH<c=28,font=/HTQHQB+TimesNewRomanPS-ItalicMT>",
            ["GLYPH<c="],
            True,
        ),
        (
            "This is normal text without any artifacts.",
            ["GLYPH<c="],
            False,
        ),
    ],
)
def test_contains_any(text: str, patterns: list[str], output: bool):
    """Test identifying formatting artifacts."""
    actual = contains_any(text, patterns)
    assert actual == output
