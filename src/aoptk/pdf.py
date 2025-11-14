
class PDF:
    def __init__(self, path: str):
        self.path = path

    def __str__(self) -> str:
        return self.path