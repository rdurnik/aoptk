from aoptk.provide_normalization_dataframe import ProvideNormalizationDataframe
import pandas as pd


class ProvideMeshTermDataframeFromCSV(ProvideNormalizationDataframe):
    def __init__(self, database_path: str):
        self._database_path = database_path

    def provide_normalization_dataframe(self):
        mesh_term_database = pd.read_csv(self._database_path)
        mesh_term_database['heading'] = (
            mesh_term_database['heading']
            .astype(str)
            .str.lower()
        )
        mesh_term_database['mesh_terms'] = (
            mesh_term_database['mesh_terms']
            .astype(str)
            .str.lower()
            .str.split(',')
            .apply(lambda x: [term.strip() for term in x]) 
        )
        return mesh_term_database
