from aoptk.normalize_chemical import NormalizeChemical
import pandas as pd


class MeshTerms(NormalizeChemical):
    def __init__(self, mesh_terms: pd.DataFrame):
        self._mesh_terms = mesh_terms

    def normalize_chemical(self, chemical):
        for _, row in self._mesh_terms.iterrows():
            heading = row.loc['heading']
            if heading == chemical:
                return heading
            entry_terms = row.loc['entry_terms']
            terms = [t.strip() for t in str(entry_terms).split(';') if t.strip()]
            if chemical in terms:
                return heading
        return chemical

# This is a preliminary version of the database. We need to get database with all the MeSH terms.
    def get_database_for_normalization(self, mesh_term_database_path = '/home/rdurnik/aoptk/databases/tox21_tggates_mesh_terms.xlsx'):
        mesh_term_database = pd.read_excel(mesh_term_database_path)
        return mesh_term_database
    
    def clean_database_for_normalization(self, mesh_term_database):
        mesh_term_database = mesh_term_database.dropna(subset=['entry_terms'])
        mesh_term_database.loc[:, 'heading'] = mesh_term_database['heading'].str.lower()
        mesh_term_database.loc[:, 'entry_terms'] = mesh_term_database['entry_terms'].str.lower()
        return mesh_term_database




    