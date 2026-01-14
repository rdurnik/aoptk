from __future__ import annotations


class Chemical:
    """Data structure representing a chemical.

    Instances are considered equal when their `name` values are equal.
    The class implements ``__hash__`` so instances can be used as dict keys
    or set members.
    """

    def __init__(self, name: str):
        """Create a `Chemical`.

        Args:
            name: The given name of the chemical.
        """
        self._name = name
        self._heading: str | None = None
        self._synonyms: set[str] = set()

    @property
    def synonyms(self) -> set[str]:
        """Synonyms of the chemical.

        Returns:
            set[str]: All synonyms of the chemical.
        """
        return self._synonyms

    @property
    def heading(self) -> str | None:
        """Heading or canonical name of the chemical.

        Only available after normalization or if it is set manually after object instantiation.

        Returns:
            str | None: Canonical name of the chemical or None
        """
        return self._heading

    @heading.setter
    def heading(self, value: str) -> None:
        """Set the canonical name or heading of the chemical.

        Args:
            value (str): Canonical name or heading to use
        """
        self._heading = value

    @property
    def name(self) -> str:
        """Return the chemical's name."""
        return self._name

    def __all_names(self) -> set[str]:
        """Get all names for the chemical.

        Returns:
            set[str]: Union of synonyms, name and heading.
        """
        all_names = self._synonyms.union([self._name])
        if self._heading:
            all_names.add(self._heading)
        return all_names

    def similar(self, other: Chemical) -> bool:
        """Test if two chemicals are similar, so if any of their names match.

        Chemicals that are equal are also always similar.

        Args:
            other (Chemical): Chemical to compare to.

        Returns:
            bool: True if any of the names match, False otherwise.
        """
        return not self.__all_names().isdisjoint(other.__all_names())

    def __str__(self) -> str:
        """Return a human-friendly string for the chemical (its name)."""
        return self._name

    def __eq__(self, other: object) -> bool:
        """Compare two Chemical instances for equality.

        Returns ``NotImplemented`` when `other` is not a `Chemical`, allowing
        Python to try reflected comparisons or fall back to ``False``.
        """
        if not isinstance(other, Chemical):
            return self.__eq_object(other)
        return self.__eq_chemical(other)

    def __eq_chemical(self, other: Chemical) -> bool:
        """Private helper to compare two chemicals.

        Args:
            other (Chemical): Chemical to compare.

        Returns:
            bool: If headings are present, is true if heading matches. Otherwise use given name instead.
        """
        this_name = self.heading if self.heading else self.name
        other_name = other.heading if other.heading else other.name
        return this_name == other_name

    def __eq_object(self, other: object) -> bool:
        """Private helper to compare a Chemical to a non-Chemical object.

        This is called from :meth:`__eq__` when ``other`` is not a
        :class:`Chemical`. The method compares the string representation of
        ``other`` to this instance's heading (when present) and name.

        Args:
            other (object): Object to compare. Its ``str()`` value is used
                for the comparison.

        Returns:
            bool: ``True`` if the string representation of ``other`` equals
            the chemical's heading (if set) or name, ``False`` otherwise.
        """
        heading_equal = self.heading == str(other) if self.heading else False
        name_equal = self.name == str(other)
        return heading_equal or name_equal

    def __hash__(self) -> int:
        """Return a hash based on the chemical name.

        This ensures objects that compare equal also have the same hash,
        which is required for correct behaviour in sets and dict keys.
        """
        return hash(self.name)
