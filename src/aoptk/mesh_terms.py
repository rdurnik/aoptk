import pandas as pd
from aoptk.normalize_chemical import NormalizeChemical


class MeshTerms(NormalizeChemical):
    """Class for normalizing chemical names using MeSH terms."""

    def __init__(self, mesh_terms: pd.DataFrame):
        self._mesh_terms = mesh_terms

    def normalize_chemical(self, chemical: str) -> str:
        """Normalize a chemical name using MeSH terms."""
        for _, row in self._mesh_terms.iterrows():
            heading = row.loc["heading"]
            if heading == chemical:
                return heading
            mesh_terms = row.loc["mesh_terms"]
            if chemical in mesh_terms:
                return heading
        return chemical
