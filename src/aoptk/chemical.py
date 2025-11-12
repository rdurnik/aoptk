class Chemical:
    def __init__(self, chemical_name: str):
        self.chemical_name = chemical_name

    def __str__(self) -> str:
        return self.chemical_name
