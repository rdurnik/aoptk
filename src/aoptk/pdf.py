import pandas as pd

class PDF:
    def __init__(self, pdf: pd.DataFrame):
        self.pdf = pdf
    
    def __str__(self) -> pd.DataFrame:
        return self.pdf
