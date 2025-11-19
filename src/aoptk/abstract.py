class Abstract:
    def __init__(self, text: str):
        self.text = text

    def __str__(self) -> str:
        return self.text