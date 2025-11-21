class Chemical:
    """Data structure representing a chemical."""

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return self._name

    def __eq__(self, other) -> bool:
        return self.name == other.name
