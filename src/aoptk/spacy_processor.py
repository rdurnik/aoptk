from __future__ import annotations
from typing import ClassVar
import spacy
from aoptk.chemical import Chemical
from aoptk.find_chemical import FindChemical
from aoptk.sentence import Sentence
from aoptk.sentence_generator import SentenceGenerator
from scispacy.linking import EntityLinker


class Spacy(FindChemical, SentenceGenerator):
    """Process text using Spacy package."""

    _models: ClassVar[dict[str, object]] = {}
    _mesh_terms_config: ClassVar[dict[str, bool | str]] = {"resolve_abbreviations": True, "linker_name": "mesh"}

    def __init__(self, model: str = "en_ner_bc5cdr_md", mesh_model: str = "en_ner_bc5cdr_md"):
        """Initialize with a spaCy model."""
        self.model = model
        self.mesh_model = mesh_model
        if model not in Spacy._models:
            Spacy._models[model] = spacy.load(model)
        self.nlp = Spacy._models[model]
        if mesh_model not in Spacy._models:
            Spacy._models[mesh_model] = spacy.load(mesh_model)
        self.nlp_mesh = Spacy._models[mesh_model]
        if "scispacy_linker" not in self.nlp_mesh.pipe_names:
            self.nlp_mesh.add_pipe("scispacy_linker", config=Spacy._mesh_terms_config)

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
            sentences.append(s)
        return sentences

    def generate_mesh_terms(self, text: str) -> list[str]:
        """Generate MeSH terms from the given text using Scispacy entity linking."""
        mesh_terms = []
        mesh_doc = self.nlp_mesh(text)

        if mesh_doc.ents:
            entity = mesh_doc.ents[0]
            mesh_linker = self.nlp_mesh.get_pipe("scispacy_linker")
            aliases = []
            for cui, _ in entity._.kb_ents:
                mesh_info = mesh_linker.kb.cui_to_entity[cui]
                aliases.extend(mesh_info.aliases)
            mesh_terms = sorted({alias.lower() for alias in aliases})

        return mesh_terms

