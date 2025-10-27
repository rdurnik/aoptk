from aoptk.normalize_chemical import NormalizeChemical
import pandas as pd


class PubChemSynonyms(NormalizeChemical):
    def __init__(self, synonyms: pd.DataFrame):
        self._synonyms = synonyms

    def normalize_chemical(self, chemical):
        for _, row in self._synonyms.iterrows():
            heading = row.loc['heading']
            if heading == chemical:
                return heading
            synonyms = row.loc['synonyms']
            if chemical in synonyms:
                return heading
        return chemical
