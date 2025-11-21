class PDF:
    """Data structure representing a PDF file."""

    def __init__(self, path: str):
        self.path = path

    def __str__(self) -> str:
        return self.path
