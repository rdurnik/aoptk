from aoptk.literature.id import ID


class Abstract:
    """Abstract data structure containing the text of the abstract."""

    def __init__(self, text: str, publication_id: ID):
        self.text = text
        self.publication_id = publication_id

    def __str__(self) -> str:
        return self.text
