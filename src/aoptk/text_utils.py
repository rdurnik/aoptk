def ends(text: str) -> bool:
    """Check if text ends with sentence-ending punctuation.

    Args:
        text (str): The text to check.
        sentence_terminators (list[str] | None): List of sentence terminators.
    """
    stripped = text.rstrip()
    return any(stripped.endswith(x) for x in [".", "!", "?", "]"])


def endswith_digit(text: str) -> bool:
    """Check if text ends with a digit.

    Args:
        text (str): The text to check.
    """
    stripped = text.rstrip()
    return stripped[-1].isdigit()


def end_of_span(text: str) -> bool:
    """Check text whether it is the end of a span.

    Args:
        text (str): Text to check

    Returns:
        bool: True if text has common delimiter or ends with a digit.
    """
    return ends(text) or endswith_digit(text)


def contains_any(text: str, substrs: list[str]) -> bool:
    """Check if text looks like formatting artifacts.

    Args:
        text (str): The text to check.
        substrs (list[str] | None): substrings to match.
    """
    return any(match in text for match in substrs)
