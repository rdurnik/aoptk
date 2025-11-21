from aoptk.find_chemical import FindChemical
from aoptk.chemical import Chemical
import spacy
import scispacy

class ScispacyFindChemical(FindChemical):
    def __init__(self, model: str = 'en_ner_bc5cdr_md'):
        self.model = model
        self.nlp = spacy.load(self.model)

    def find_chemical(self, sentence: str) -> list[Chemical]:
        doc = self.nlp(sentence)
        for ent in doc.ents:
            if ent.label_ == "CHEMICAL":
                return [Chemical(chemical_name=ent.text.lower())]
        return [Chemical(chemical_name="")]