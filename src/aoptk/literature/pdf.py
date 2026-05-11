from pathlib import Path


class PDF:
    """Data structure representing a PDF file."""

    def __init__(self, path: Path):
        self.path = path

    def __str__(self) -> str:
        return str(self.path)
