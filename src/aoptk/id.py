class ID:
    def __init__(self, id_str: str):
        self.id_str = id_str

    def __str__(self) -> str:
        return self.id_str


class PubMedID(ID):
    def __init__(self, id_str: str):
        super().__init__(id_str)

    def __str__(self) -> str:
        return f"PubMedID: {self.id_str}"