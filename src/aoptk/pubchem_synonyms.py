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
            terms = [t.strip() for t in str(synonyms).split(';') if t.strip()]
            if chemical in terms:
                return heading
        return chemical

# This is a preliminary version of the database. We need to get database with all the data from PubChem...
    def get_database_for_normalization(self, pubchem_synonyms_database_path = '/home/rdurnik/aoptk/databases/pubchem_synonyms.xlsx'):
        pubchem_synonyms_database = pd.read_excel(pubchem_synonyms_database_path)
        return pubchem_synonyms_database
    
    def clean_database_for_normalization(self, pubchem_synonyms_database):
        pubchem_synonyms_database = pubchem_synonyms_database.dropna(subset=['synonyms'])
        pubchem_synonyms_database.loc[:, 'heading'] = pubchem_synonyms_database['heading'].str.lower()
        pubchem_synonyms_database.loc[:, 'synonyms'] = pubchem_synonyms_database['synonyms'].str.lower()
        return pubchem_synonyms_database
