from __future__ import annotations
from typing import TYPE_CHECKING
from typing import ClassVar
import spacy
from scispacy.linking import EntityLinker
from aoptk.chemical import Chemical
from aoptk.find_chemical import FindChemical
from aoptk.normalization.normalize_chemical import NormalizeChemical
from aoptk.sentence import Sentence
from aoptk.sentence_generator import SentenceGenerator

if TYPE_CHECKING:
    from scispacy.linking import EntityLinker


class Spacy(FindChemical, SentenceGenerator, NormalizeChemical):
    """Process text using Spacy package."""

    descriptive_suffixes: ClassVar[list[str]] = [
        "induced",
        "mediated",
        "associated",
        "related",
        "dependent",
        "treated",
        "exposed",
        "caused",
        "driven",
        "linked",
        "based",
    ]

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
        chemicals = []
        for ent in doc.ents:
            if ent.label_ == "CHEMICAL":
                trimmed_name = self._trim_name(ent.text.lower())
                chemicals.append(Chemical(name=trimmed_name))
        return chemicals

    def _trim_name(self, name: str) -> str:
        """Return the chemical name with non-chemical suffixes after dashes trimmed.

        - Preserves legitimate hyphenated chemical names (e.g., "n-acetyl-l-cysteine").
        - Trims descriptors starting after a dash when the first token is a known suffix
          (e.g., "carbon tetrachloride-induced ..." -> "carbon tetrachloride").
        - Removes a trailing dash at the end of the name.
        """
        name = self._remove_trailing_dash(name.strip())
        if "-" not in name:
            return name
        parts = name.split("-")
        idx = self._first_descriptive_suffix_index(parts)
        return "-".join(parts[:idx]).strip() if idx is not None else name

    def _remove_trailing_dash(self, name: str) -> str:
        """Remove a trailing dash from `name` if present, preserving valid hyphenations."""
        return name[:-1].strip() if name.endswith("-") else name

    def _first_descriptive_suffix_index(self, parts: list[str]) -> int | None:
        """Return index of first descriptive suffix segment in `parts`, else None.

        `parts` is the dash-split of the name; index 0 is the base chemical segment.
        """
        return next(
            (i for i, part in enumerate(parts[1:], start=1) if self._first_token_is_descriptive_suffix(part)),
            None,
        )

    def _first_token_is_descriptive_suffix(self, part: str) -> bool:
        """Check whether the first token of a dash-separated `part` is a descriptive suffix."""
        token = part.strip().split()[0] if part.strip() else ""
        return token in self.descriptive_suffixes

    def tokenize(self, text: str) -> list[Sentence]:
        """Use spaCy to generate sentences."""
        doc = self.nlp(text)
        sentences = []
        for sent in doc.sents:
            sent_text = sent.text.strip()
            s = Sentence(sent_text)
            sentences.append(s)
        return sentences

    def normalize_chemical(self, chemical: Chemical) -> Chemical:
        """Normalize the chemical name.

        Generate MeSh terms for the given chemical name and return the first relevant chemical.
        """
        if mesh_terms := Spacy().generate_mesh_terms(chemical.name):
            chemical.synonyms.clear()
            chemical.synonyms.update(mesh_terms)
        return chemical

    def generate_mesh_terms(self, text: str) -> list[str]:
        """Generate MeSH terms from the given text using Scispacy entity linking."""
        mesh_terms = []
        mesh_doc = self.nlp_mesh(text)

        if mesh_doc.ents:
            entity = mesh_doc.ents[0]
            mesh_linker: EntityLinker = self.nlp_mesh.get_pipe("scispacy_linker")
            aliases = []
            for cui, _ in entity._.kb_ents:
                mesh_info = mesh_linker.kb.cui_to_entity[cui]
                aliases.extend(mesh_info.aliases)
            mesh_terms = sorted({alias.lower() for alias in aliases})

        return mesh_terms
