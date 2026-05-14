import xml.etree.ElementTree as ET
import pandas as pd
from aoptk.normalization.provide_normalization_dataframe import ProvideNormalizationDataframe


class ProvideMeshTermDataframeFromXML(ProvideNormalizationDataframe):
    """Class to provide MeSH term normalization dataframe from XML."""

    def __init__(self, database_path: str):
        self._database_path = database_path

    def provide_normalization_dataframe(self) -> pd.DataFrame:
        """Parse the XML file and create a DataFrame for MeSH term normalization."""
        tree = ET.parse(self._database_path)
        root = tree.getroot()
        name_space = {"name_space": "https://www.nlm.nih.gov/mesh"}
        rows = []
        for record in root.findall(".//DescriptorRecord", name_space):
            heading_element = record.find(".//DescriptorName/String", name_space)
            if heading_element is None:
                continue
            heading_text = heading_element.text or ""
            heading = heading_text.strip().lower()

            terms = []
            for term in record.findall(".//TermList/Term/String", name_space):
                term_text = term.text or ""
                term_element = term_text.strip().lower()
                if term_element and term_element != heading:
                    terms.append(term_element)
            rows.append([heading, terms])

        return pd.DataFrame(rows, columns=["heading", "mesh_terms"])
