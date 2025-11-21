from __future__ import annotations
from typing import ClassVar
import spacy
from aoptk.chemical import Chemical
from aoptk.find_chemical import FindChemical


class ScispacyFindChemical(FindChemical):
    """Find chemicals in text using SciSpacy."""

    _models: ClassVar[dict[str, object]] = {}

    def __init__(self, model: str = "en_ner_bc5cdr_md"):
        """Initialize with a spaCy model."""
        self.model = model
        if model not in ScispacyFindChemical._models:
            ScispacyFindChemical._models[model] = spacy.load(model)
        self.nlp = ScispacyFindChemical._models[model]

    def find_chemical(self, sentence: str) -> list[Chemical]:
        """Find chemicals in the given sentence."""
        doc = self.nlp(sentence)
        return [Chemical(name=ent.text.lower()) for ent in doc.ents if ent.label_ == "CHEMICAL"]
