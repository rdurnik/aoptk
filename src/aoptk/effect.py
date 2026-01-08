class Effect:
    """Data structure representing a biological effect (adverse outcome / key event)."""

    def __init__(self, name: str):
        """Create an `Effect`.

        Args:
            name: The canonical name of the effect.
        """
        self._name = name

    @property
    def name(self) -> str:
        """Return the effect's name."""
        return self._name

    def __str__(self) -> str:
        """Return a human-friendly string for the effect (its name)."""
        return self.name

    def __eq__(self, other: object) -> bool:
        """Compare two Effect instances for equality."""
        if not isinstance(other, Effect):
            return self.name == str(other)
        return self.name == other.name

    def __hash__(self) -> int:
        """Return a hash based on the effect name."""
        return hash(self.name)
