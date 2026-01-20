from __future__ import annotations
from pydoc import text
from typing import TYPE_CHECKING
from typing import ClassVar
import spacy
from aoptk.literature.publication import Publication
from aoptk.literature.pdf import PDF
from pathlib import Path
from aoptk.literature.id import ID
from aoptk.literature.abstract import Abstract
from spacy_layout import spaCyLayout
from aoptk.literature.pdf_parser import PDFParser
import re



class SpacyPDF(PDFParser):
    """Process PDF using Spacy package."""

    _models: ClassVar[dict[str, object]] = {}

    def __init__(self, pdfs: list[PDF], model: str = "en", figures_output_dir: str = "tests/figure_storage"):
        """Initialize with a spaCy model."""
        self.pdfs = pdfs
        self.figures_output_dir = figures_output_dir
        self.model = model
        if model not in SpacyPDF._models:
            SpacyPDF._models[model] = spacy.blank(model)
        self.nlp = spacy.blank(model)
        self.layout = spaCyLayout(self.nlp)
    
    def get_publications(self) -> list[Publication]:
        """Get a list of publications."""
        pubs = []
        sources = [(Path(pdf.path), pdf) for pdf in self.pdfs]
        for doc, pdf in self.layout.pipe(sources, as_tuples=True):
            pub = self._parse_doc_pdf(doc, pdf)
            pubs.append(pub)
        return pubs

    def _parse_doc_pdf(self, doc, pdf: PDF) -> Publication:
        """Parse a single PDF and return a Publication object."""
        publication_id = ID(Path(pdf.path).stem)
        abstract = self._parse_abstract(doc, publication_id)
        full_text = self._parse_full_text(doc)
        abbreviations = self._extract_abbreviations(doc)
        figures = []  # PymupdfParser._extract_figures(pdf)
        figure_descriptions = self._extract_figure_descriptions(doc)
        tables = self._extract_tables(doc)
        return Publication(
            id=publication_id,
            abstract=abstract,
            full_text=full_text,
            abbreviations=abbreviations,
            figures=figures,
            figure_descriptions=figure_descriptions,
            tables=tables,
        )

    def _parse_full_text(self, doc) -> list[str]:
        merged_spans = []
        accumulated_text = ""
        
        for span in doc.spans["layout"]:
            if self._is_page_header_footer(span.text) or self._is_formatting(accumulated_text) or self._contains_email(span.text) or span.label_ != "text":
                continue
            
            if accumulated_text:
                accumulated_text += " " + span.text
            else:
                accumulated_text = span.text
            
            if self._ends_with_sentence_terminator(accumulated_text) or self._ends_with_year(accumulated_text):
                merged_spans.append(accumulated_text)
                accumulated_text = ""
        
        if accumulated_text:
            merged_spans.append(accumulated_text)
        
        return merged_spans

    def _is_page_header_footer(self, 
                                text: str,
                                max_text_length: int = 60, 
                                running_header_indicators: list[str] = ["et al."],
                                doi_pattern: str = r'\b10\.\d{4,}/\S+\b',
                        ) -> bool:
        """Check if text looks like a running page header."""
        return (
        len(text) < max_text_length
        and any(indicator in text for indicator in running_header_indicators) or bool(re.search(doi_pattern, text)))
    
    def _is_formatting(self, 
                       text: str, 
                       formatting_indicators: list[str] = ["GLYPH<c="]
                        ) -> bool:
        """Check if text looks like formatting artifacts."""
        return any(indicator in text for indicator in formatting_indicators)
    
    def _contains_email(self, text: str) -> bool:
        """Check if text contains an email address."""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return bool(re.search(email_pattern, text))

    def _ends_with_sentence_terminator(self,
                                       text: str,
                                       sentence_terminators: list[str] = [".", 
                                                                          "!", 
                                                                          "?"],
                                       ) -> bool:
        """Check if text ends with sentence-ending punctuation."""
        stripped = text.rstrip()
        return stripped[-1] in sentence_terminators
    
    def _ends_with_year(self,
                       text: str) -> bool:
        """Check if text ends with a year (four-digit number)."""
        stripped = text.rstrip()
        return len(stripped) >= 4 and stripped[-4:].isdigit()

    def _parse_abstract(self, doc, publication_id: ID) -> Abstract:
        """Extract the abstract from the PDF text."""
        page_layout, page_spans = doc._.pages[0] 
        largest_span = max(page_spans, key=lambda span: len(span.text) if hasattr(span, 'text') else 0, default=None)
        abstract_text = largest_span.text if largest_span else ""
        return Abstract(text=abstract_text, publication_id=publication_id)

    def _extract_figure_descriptions(self, doc):
        figure_descriptions = []
        for span in doc.spans["layout"]:
            if span.label_ == "caption":
                figure_descriptions.append(span.text)                
        return figure_descriptions
    
    def _extract_tables(self, doc):
        return []

    def _extract_abbreviations(self, doc):
        return {}