import pandas as pd
from aoptk.normalize_chemical import NormalizeChemical


class PubChemSynonyms(NormalizeChemical):
    """Class for normalizing chemical names using PubChem synonyms."""
    def __init__(self, synonyms: pd.DataFrame):
        self._synonyms = synonyms

    def normalize_chemical(self, chemical: str) -> str:
        """Normalize a chemical name using PubChem synonyms."""
        for _, row in self._synonyms.iterrows():
            heading = row.loc["heading"]
            if heading == chemical:
                return heading
            synonyms = row.loc["synonyms"]
            if chemical in synonyms:
                return heading
        return chemical
