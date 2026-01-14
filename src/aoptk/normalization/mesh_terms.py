import pandas as pd
from aoptk.chemical import Chemical
from aoptk.normalization.normalize_chemical import NormalizeChemical


class MeshTerms(NormalizeChemical):
    """Class for normalizing chemical names using MeSH terms."""

    def __init__(self, mesh_terms: pd.DataFrame):
        self._mesh_terms = mesh_terms

    def normalize_chemical(self, chemical: Chemical) -> Chemical:
        """Normalize a chemical name using MeSH terms."""
        for _, row in self._mesh_terms.iterrows():
            heading = row.loc["heading"]
            if heading == chemical.name or chemical.name in row.loc["mesh_terms"]:
                chemical.heading = heading
                chemical.synonyms.clear()
                chemical.synonyms.update(row.loc["mesh_terms"])
                return chemical
        return chemical
