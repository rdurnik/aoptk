from __future__ import annotations
import re
from pathlib import Path
from typing import ClassVar
import pandas as pd
import spacy
from spacy_layout import spaCyLayout
from aoptk.literature.abstract import Abstract
from aoptk.literature.id import ID
from aoptk.literature.pdf import PDF
from aoptk.literature.publication import Publication
from aoptk.literature.pymupdf_parser import PymupdfParser


class SpacyPDF(PymupdfParser):
    """Process PDF using Spacy package."""

    _models: ClassVar[dict[str, object]] = {}

    def __init__(self, pdfs: list[PDF], model: str = "en", figures_output_dir: str = "tests/figure_storage"):
        """Initialize with a spaCy model.

        Args:
            pdfs (list[PDF]): List of PDF objects to process.
            model (str): spaCy model to use.
            figures_output_dir (str): Directory to store extracted figures.
        """
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

    def _parse_doc_pdf(self, doc: object, pdf: PDF) -> Publication:
        """Parse a single PDF and return a Publication object.

        Args:
            doc (object): The spaCy document object.
            pdf (PDF): The PDF object.
        """
        publication_id = ID(Path(pdf.path).stem)
        abstract = self._parse_abstract(doc, publication_id)
        full_text = self._parse_full_text(doc)
        abbreviations = {}
        figures = self._extract_figures(pdf)
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

    def _parse_full_text(self, doc: object) -> list[str]:
        """Extract the full text from the PDF.

        Args:
            doc (object): The spaCy document object.
        """
        first_page_spans = self._extract_first_page_spans(doc)
        remaining_pages_spans = self._extract_remaining_pages_spans(doc)

        return first_page_spans + remaining_pages_spans

    def _extract_first_page_spans(self, doc: object) -> list[str]:
        """Extract text spans from the first page of the PDF.

        Args:
            doc (object): The spaCy document object.
        """
        _, page_spans = doc._.pages[0]
        return [span.text for span in page_spans if span.label_ == "text"]

    def _extract_remaining_pages_spans(self, doc: object) -> list[str]:
        """Extract text spans from the remaining pages of the PDF.

        Args:
            doc (object): The spaCy document object.
        """
        remaining_pages_spans = []
        remaining_pages = doc._.pages[1:]
        if accumulated_text := self._extract_accumulated_text_across_pages(remaining_pages_spans, remaining_pages):
            remaining_pages_spans.append(accumulated_text)
        return remaining_pages_spans

    def _extract_accumulated_text_across_pages(
        self,
        remaining_pages_spans: list[object],
        remaining_pages: list[object],
    ) -> str:
        """Accumulate text across pages until a boundary is reached.

        Args:
            remaining_pages_spans (list[object]): List to store accumulated spans.
            remaining_pages (list[object]): List of remaining pages.
        """
        accumulated_text = ""
        for _, page_spans in remaining_pages:
            for span in page_spans:
                if self._should_skip_span(span):
                    continue
                accumulated_text = self._append_text(accumulated_text, span.text)
                if self._is_span_boundary(accumulated_text):
                    remaining_pages_spans.append(accumulated_text)
                    accumulated_text = ""
        return accumulated_text

    def _should_skip_span(self, span: object) -> bool:
        """Check if span should be skipped based on various criteria.

        Args:
            span (object): The text span object.
        """
        return span.label_ != "text" or self._is_page_header_footer(span.text) or self._is_formatting(span.text)

    def _append_text(self, accumulated: str, new_text: str) -> str:
        """Append new text to accumulated text with proper spacing.

        Args:
            accumulated (str): The accumulated text so far.
            new_text (str): The new text to append.
        """
        return f"{accumulated} {new_text}" if accumulated else new_text

    def _is_span_boundary(self, text: str) -> bool:
        """Check if text marks the end of a span.

        Args:
            text (str): The text to check.
        """
        return self._ends_with_sentence_terminator(text) or self._has_digit_at_the_end(text)

    def _is_page_header_footer(
        self,
        text: str,
        max_text_length: int = 60,
        running_header_indicators: list[str] | None = None,
        doi_pattern: str = r"\b10\.\d{4,}/\S+\b",
    ) -> bool:
        """Check if text looks like a running page header.

        Args:
            text (str): The text to check.
            max_text_length (int): Maximum length for header/footer text.
            running_header_indicators (list[str] | None): Indicators of running headers.
            doi_pattern (str): Regex pattern to identify DOIs.
        """
        if running_header_indicators is None:
            running_header_indicators = ["et al."]
        return (
            len(text) < max_text_length and any(indicator in text for indicator in running_header_indicators)
        ) or bool(re.search(doi_pattern, text))

    def _is_formatting(
        self,
        text: str,
        formatting_indicators: list[str] | None = None,
    ) -> bool:
        """Check if text looks like formatting artifacts.

        Args:
            text (str): The text to check.
            formatting_indicators (list[str] | None): Indicators of formatting artifacts.
        """
        if formatting_indicators is None:
            formatting_indicators = ["GLYPH<c="]
        return any(indicator in text for indicator in formatting_indicators)

    def _ends_with_sentence_terminator(
        self,
        text: str,
        sentence_terminators: list[str] | None = None,
    ) -> bool:
        """Check if text ends with sentence-ending punctuation.

        Args:
            text (str): The text to check.
            sentence_terminators (list[str] | None): List of sentence terminators.
        """
        if sentence_terminators is None:
            sentence_terminators = [".", "!", "?", "]"]
        stripped = text.rstrip()
        return stripped[-1] in sentence_terminators

    def _has_digit_at_the_end(self, text: str) -> bool:
        """Check if text is a digit.

        Args:
            text (str): The text to check.
        """
        stripped = text.rstrip()
        return stripped[-1].isdigit()

    def _parse_abstract(self, doc: object, publication_id: ID) -> Abstract:
        """Extract the abstract from the PDF text.

        Args:
            doc (object): The spaCy document object.
            publication_id (ID): The publication ID.
        """
        _, page_spans = doc._.pages[0]
        largest_span = max(page_spans, key=lambda span: len(span.text) if hasattr(span, "text") else 0, default=None)
        abstract_text = largest_span.text if largest_span else ""
        if not self._ends_with_sentence_terminator(largest_span.text):
            rest_of_the_abstract = next(
                (
                    span.text
                    for span in page_spans
                    if span != largest_span and self._ends_with_sentence_terminator(span.text)
                ),
                "",
            )
            abstract_text += " " + rest_of_the_abstract
        return Abstract(text=abstract_text, publication_id=publication_id)

    def _extract_figure_descriptions(self, doc: object) -> list[str]:
        """Extract figure descriptions from the PDF.

        Args:
            doc (object): The spaCy document object.
        """
        return [span.text for span in doc.spans["layout"] if span.label_ == "caption"]

    def _extract_tables(self, doc: object) -> list[pd.DataFrame]:
        """Extract tables from the PDF.

        Args:
            doc (object): The spaCy document object.
        """
        return [table._.data for table in doc._.tables]
