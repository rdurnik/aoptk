import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aoptk.provide_normalization_dataframe import ProvideNormalizationDataframe
import pandas as pd
import xml.etree.ElementTree as ET

pd.set_option('display.max_colwidth', None)

class ProvideMeshTermDataframeFromXML(ProvideNormalizationDataframe):
    def __init__(self, database_path: str):
        self._database_path = database_path

    def provide_normalization_dataframe(self):
        tree = ET.parse(self._database_path)
        root = tree.getroot()
        name_space = {"name_space": "http://www.nlm.nih.gov/mesh"}
        rows = []
        for record in root.findall(".//DescriptorRecord", name_space):
            heading_element = record.find(".//DescriptorName/String", name_space)
            if heading_element is None:
                continue
            heading = heading_element.text.strip().lower()
            
            terms = []
            for term in record.findall(".//TermList/Term/String", name_space):
                term_name = term.text.strip().lower()
                if term_name and term_name != heading:
                    terms.append(term_name)
            rows.append([heading, terms])
        
        return pd.DataFrame(rows, columns=['heading', 'mesh_terms'])

print(ProvideMeshTermDataframeFromXML('/home/rdurnik/aoptk/tests/test_mesh_terms_database.xml').provide_normalization_dataframe())