class ID:
    """Base class for different types of publication IDs."""

    def __init__(self, id_str: str):
        self.id_str = id_str

    def __str__(self) -> str:
        return self.id_str

    def __eq__(self, other: object) -> bool:
        """Compare IDs by their string value."""
        if isinstance(other, ID):
            return self.id_str == other.id_str
        if isinstance(other, str):
            return self.id_str == other
        return False

    def __hash__(self) -> int:
        """Hash based on string value for use in sets/dicts."""
        return hash(self.id_str)


class PMCID(ID):
    """PubMed Central ID."""

    def __init__(self, id_str: str):
        super().__init__(id_str)

    def __str__(self) -> str:
        return f"PMCID: {self.id_str}"


class PMID(ID):
    """PubMed ID."""

    def __init__(self, id_str: str):
        super().__init__(id_str)

    def __str__(self) -> str:
        return f"PMID: {self.id_str}"


class DOI(ID):
    """Digital Object Identifier."""

    def __init__(self, id_str: str):
        super().__init__(id_str)

    def __str__(self) -> str:
        return f"DOI: {self.id_str}"
