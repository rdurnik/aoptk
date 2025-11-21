class Chemical:
    """Data structure representing a chemical.

    Instances are considered equal when their `name` values are equal.
    The class implements ``__hash__`` so instances can be used as dict keys
    or set members.
    """

    def __init__(self, name: str):
        """Create a `Chemical`.

        Args:
            name: The canonical name of the chemical.
        """
        self._name = name

    @property
    def name(self) -> str:
        """Return the chemical's name."""
        return self._name

    def __str__(self) -> str:
        """Return a human-friendly string for the chemical (its name)."""
        return self._name

    def __eq__(self, other: object) -> bool:
        """Compare two Chemical instances for equality.

        Returns ``NotImplemented`` when `other` is not a `Chemical`, allowing
        Python to try reflected comparisons or fall back to ``False``.
        """
        if not isinstance(other, Chemical):
            return self.name == str(other)
        return self.name == other.name

    def __hash__(self) -> int:
        """Return a hash based on the chemical name.

        This ensures objects that compare equal also have the same hash,
        which is required for correct behaviour in sets and dict keys.
        """
        return hash(self.name)
