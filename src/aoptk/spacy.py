from __future__ import annotations
from typing import ClassVar
import spacy
from aoptk.chemical import Chemical
from aoptk.find_chemical import FindChemical
from aoptk.sentence import Sentence
from aoptk.sentence_generator import SentenceGenerator


class Spacy(FindChemical, SentenceGenerator):
    """Process text using Spacy package."""

    _models: ClassVar[dict[str, object]] = {}

    def __init__(self, model: str = "en_ner_bc5cdr_md"):
        """Initialize with a spaCy model."""
        self.model = model
        if model not in Spacy._models:
            Spacy._models[model] = spacy.load(model)
        self.nlp = Spacy._models[model]

    def find_chemical(self, sentence: str) -> list[Chemical]:
        """Find chemicals in the given sentence."""
        doc = self.nlp(sentence)
        return [Chemical(name=ent.text.lower()) for ent in doc.ents if ent.label_ == "CHEMICAL"]

    def tokenize(self, text: str) -> list[Sentence]:
        """Use spaCy to generate sentences."""
        doc = self.nlp(text)
        sentences = []
        for sent in doc.sents:
            sent_text = sent.text.strip()
            s = Sentence(sent_text)
            ents = getattr(sent, "ents", ())
            s.entities = [(ent.text, ent.label_) for ent in ents] if ents else []
            sentences.append(s)
        return sentences
