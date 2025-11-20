from aoptk.find_chemical import FindChemical
from aoptk.chemical import Chemical
import spacy
import scispacy

class ScispacyFindChemical(FindChemical):
    def __init__(self, sentences: list[str]):
        self._sentences = sentences

    def find_chemical(self) -> list[Chemical]:
        chem_list = []
        for sentence in self._sentences:
            chem = self.scispacy_find_chemical(sentence)
            chem_list.append(chem)
        return chem_list

    def scispacy_find_chemical(self, model = 'en_ner_bc5cdr_md') -> Chemical:
        model = spacy.load(model)
        doc = model(self._text)
        for ent in doc.ents:
            if ent.label_ == "CHEMICAL":
                return Chemical(chemical_name=ent.text.lower())
