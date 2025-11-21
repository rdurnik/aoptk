from __future__ import annotations
import spacy
from aoptk.chemical import Chemical
from aoptk.find_chemical import FindChemical


class ScispacyFindChemical(FindChemical):
    """Find chemicals in text using SciSpacy."""

    model = "en_ner_bc5cdr_md"
    nlp = spacy.load(model)

    def find_chemical(self, sentence: str) -> list[Chemical]:
        """Find chemicals in the given sentence."""
        doc = self.nlp(sentence)
        return [Chemical(name=ent.text.lower()) for ent in doc.ents if ent.label_ == "CHEMICAL"]
