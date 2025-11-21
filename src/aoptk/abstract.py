class Abstract:
    """Abstract data structure containing the text of the abstract."""

    def __init__(self, text: str):
        self.text = text

    def __str__(self) -> str:
        return self.text
