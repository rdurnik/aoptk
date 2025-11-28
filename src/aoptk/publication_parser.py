from __future__ import annotations
import re
from typing import ClassVar
import spacy
from aoptk.sentence import Sentence
from aoptk.sentence_generator import SentenceGenerator


class PublicationParser(SentenceGenerator):
    """Parse data from a given publication."""

    _models: ClassVar[dict[str, object]] = {}

    def __init__(self, text: str, model: str = "en_ner_bc5cdr_md"):
        self.text = text
        self.model = model
        if model not in PublicationParser._models:
            PublicationParser._models[model] = spacy.load(model)
        self.nlp = PublicationParser._models[model]

    def generate_sentences(self) -> list[Sentence]:
        """Return a list of sentences."""
        return self.spacy_generate_sentences()

    def spacy_generate_sentences(self) -> list[Sentence]:
        """Use spaCy to generate sentences."""
        doc = self.nlp(self.text)
        sentences = []
        for sent in doc.sents:
            sent_text = sent.text.strip()
            s = Sentence(sent_text)
            ents = getattr(sent, "ents", ())
            s.entities = [(ent.text, ent.label_) for ent in ents] if ents else []
            sentences.append(s)
        return sentences

    def regex_generate_sentences(self) -> list[Sentence]:
        """Use regex to generate sentences."""
        sentences = re.split(r"(?<=[.!?])\s+|(?<=[.!?])(?=[A-Z])|<h4>|</h4>", str(self.text))
        return [Sentence(sentence.strip()) for sentence in sentences if sentence.strip()]
