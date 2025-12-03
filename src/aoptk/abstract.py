from aoptk.id import ID

class Abstract:
    """Abstract data structure containing the text of the abstract."""

    def __init__(self, text: str, id: ID):
        self.text = text
        self.id = id

    def __str__(self) -> str:
        return self.text
