from __future__ import annotations
import re
from pathlib import Path
from typing import TYPE_CHECKING
import pymupdf
from aoptk.literature.id import ID
from aoptk.literature.pdf import PDF
from aoptk.literature.pdf_parser import PDFParser
from aoptk.literature.publication import Publication

if TYPE_CHECKING:
    from aoptk.literature.abstract import Abstract
    from aoptk.literature.pdf import PDF


class PymupdfParser(PDFParser):
    """Parse PDFs using PyMuPDF."""

    def __init__(self, pdfs: list[PDF], figures_output_dir: str = "tests/figure_storage"):
        self.figures_output_dir = figures_output_dir
        self.pdfs = pdfs
        self.pattern_abstract_written = (
            r"(?i)a\s*b\s*s\s*t\s*r\s*a\s*c\s*t\s*[:\-]?\s*(.*?)\s*"
            r"(?=\n\s*(?:keywords|introduction|1\.?\s|I\.)\b)"
        )
        self.pattern_abstract_not_written = (
            r"(?:^|\n)((?:(?!\n\s*(?:keywords?|"
            r"introduction|(?:1|I)\.?\s|section\s+1)\b).)*?)\s*"
            r"(?=\n\s*(?:keywords?|introduction|(?:1|I)\.?\s"
            r"|section\s+1)\b)"
        )
        self.pattern_figure_descriptions = r"(?ms)(?<=\n)\s*Figure\s+\d+\.?\s*(.*?)(?=\n)"
        self.pattern_any_character = r"(.*)"
        self.pattern_abbreviations = (
            r"(?i)[^\w\s]*\s*"
            r"(?:Abbreviations|Glossary)[:\s]+(.*?)"
            r"(?:\.?\s*(?:references|acknowledgement"
            r"|funding|author|conflict|ethics|"
            r"corresponding|⁎)|$)"
        )
        self.pattern_semicolon_split_between_individual_abbreviations = r";\s*"
        self.pattern_space_split_between_individual_abbreviations = (
            r"(?<=\s)(?=[A-Z0-9α-ωΑ-Ωβ]+(?:[A-Z0-9\-\u2212α-ωΑ-Ω]+)*\s+[A-Za-zα-ωΑ-Ω])"
        )
        self.pattern_comma_split_between_abbreviation_and_full_form = (
            r"([A-Za-z0-9\-α-ω"
            r"Α-Ω]+)\s*[:,]\s*(.+)"
        )

    def get_publications(self) -> list[Publication]:
        """Get a list of publications."""
        pubs = []
        for pdf in self.pdfs:
            pub = self._parse_pdf(pdf)
            pubs.append(pub)
        return pubs

    def _parse_pdf(self, pdf: PDF) -> Publication:
        """Parse a single PDF and return a Publication object."""
        text = self._extract_text_to_parse(pdf)
        publication_id = ID(Path(pdf.path).stem)
        abstract = self._parse_abstract(text)
        full_text = self._parse_full_text(text)
        abbreviations = self._extract_abbreviations(text, pdf)
        figures = self._extract_figures(pdf)
        figure_descriptions = self._extract_figure_descriptions(text)
        tables = []  # TODO
        return Publication(
            id=publication_id,
            abstract=abstract,
            full_text=full_text,
            abbreviations=abbreviations,
            figures=figures,
            figure_descriptions=figure_descriptions,
            tables=tables,
        )

    def _parse_abstract(self, text: str) -> Abstract:
        """Extract the abstract from the text."""
        if match := self._extract_abstract_match_abstract_specified(text):
            return match.group(1).strip()
        if match := self._extract_abstract_match_abstract_not_specified(text):
            match = self._remove_title_authors(match)
            return match.group(1).strip()
        if match := self._extract_first_large_paragraph(text):
            return match.group().strip()
        return None

    def _parse_full_text(self, text: str) -> str:
        """Extract the full text from the PDF text."""
        if match := self._extract_abstract_match_abstract_specified(text):
            match_end = match.end()
            return text[match_end:].strip()
        if match := self._extract_abstract_match_abstract_not_specified(text):
            match = self._remove_title_authors(match)
            match_end = match.end() + text.index(match.group(0))
            return text[match_end:].strip()
        if match := self._extract_first_large_paragraph(text):
            match_end = match.end() + text.index(match.group(0))
            return text[match_end:].strip()
        return None

    def _extract_abstract_match_abstract_specified(self, text: str) -> str:
        """Extract abstract when explicitly specified."""
        match = re.search(self.pattern_abstract_written, text, re.DOTALL)
        if match:
            return match
        return None

    def _extract_abstract_match_abstract_not_specified(self, text: str) -> str:
        """Extract abstract when not explicitly specified."""
        match = re.search(self.pattern_abstract_not_written, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match
        return None

    def _remove_title_authors(self, match: str, newlines_to_remove_from_start: int = 2) -> str:
        """Remove title and authors from the beginning of the abstract match."""
        text = match.group(1)
        parts = text.split("\n", newlines_to_remove_from_start)
        if len(parts) > newlines_to_remove_from_start:
            return re.match(self.pattern_any_character, parts[newlines_to_remove_from_start], re.DOTALL)
        return None

    def _extract_first_large_paragraph(self, text: str, large_paragraph_word_count: int = 100) -> str:
        """Extract the first large paragraph from the text."""
        paragraphs = text.split("\n")
        large_paragraphs = [p for p in paragraphs if len(p.split()) > large_paragraph_word_count]
        if large_paragraphs:
            return re.match(self.pattern_any_character, large_paragraphs[0], re.DOTALL)
        return None

    def _extract_text_to_parse(self, pdf: PDF) -> str:
        """Extract text to parse from the PDF."""
        text_to_parse = ""
        with pymupdf.open(pdf.path) as doc:
            for page in doc:
                blocks = page.get_text("blocks")
                text_to_parse += "\n".join([" ".join(block[4].split()) for block in blocks if block[4].strip()])
        return text_to_parse

    def _extract_abbreviations(self, text: str, pdf: PDF) -> dict[str, str]:
        """Extract abbreviations from the text."""
        abbreviations_dict = {}
        if match := re.search(self.pattern_abbreviations, text, re.DOTALL | re.IGNORECASE):
            abbreviation_text = match.group(1)
            if (
                entries := re.split(
                    self.pattern_semicolon_split_between_individual_abbreviations,
                    abbreviation_text.strip(),
                )
            ) and len(entries) > 1:
                abbreviations_dict = self._generate_dictionary_from_semicolon_seperated_abbreviations(entries)
            elif (
                entries := re.split(
                    self.pattern_space_split_between_individual_abbreviations,
                    abbreviation_text.strip(),
                )
            ) and len(entries) > 1:
                text_to_parse_with_preserved_newlines = self._extract_text_to_parse_abbreviations_seperated_by_newlines(
                    pdf,
                )
                abbreviations_dict = self._generate_dictionary_from_newline_seperated_abbreviations(
                    text_to_parse_with_preserved_newlines,
                )
        return abbreviations_dict

    def _generate_dictionary_from_newline_seperated_abbreviations(
        self,
        text_to_parse_with_preserved_newlines: str,
    ) -> dict[str, str]:
        """Generate abbreviation dictionary from newline-separated abbreviations."""
        abbreviations_dict = {}
        newline_match = re.search(
            self.pattern_abbreviations,
            text_to_parse_with_preserved_newlines,
            re.DOTALL | re.IGNORECASE,
        )
        if newline_match:
            abbr_text_newlines = newline_match.group(1)
            lines = [line.strip() for line in abbr_text_newlines.split("\n") if line.strip()]
            for i in range(0, len(lines) - 1, 2):
                if i + 1 < len(lines):
                    key = lines[i]
                    value = lines[i + 1]
                    abbreviations_dict[key] = value
        return abbreviations_dict

    def _generate_dictionary_from_semicolon_seperated_abbreviations(self, entries: list[str]) -> dict[str, str]:
        """Generate abbreviation dictionary from semicolon-separated abbreviations."""
        abbreviations_dict = {}
        for entry in entries:
            m = re.match(self.pattern_comma_split_between_abbreviation_and_full_form, entry.strip())
            if m:
                key, value = m.groups()
                abbreviations_dict[key.strip()] = value.strip()
            self._remove_dot_from_the_final_value(abbreviations_dict, key)
        return abbreviations_dict

    def _remove_dot_from_the_final_value(self, abbreviations_dict: dict[str, str], key: str) -> dict[str, str]:
        """Remove dot from the final value in the abbreviation dictionary."""
        k = key.strip()
        v = abbreviations_dict[k]
        if v.endswith("."):
            abbreviations_dict[k] = v[:-1].rstrip()

    def _extract_text_to_parse_abbreviations_seperated_by_newlines(self, pdf: PDF) -> str:
        """Extract text to parse, preserving newlines."""
        text_to_parse = ""
        with pymupdf.open(pdf.path) as doc:
            for page in doc:
                blocks = page.get_text("blocks")
                for block in blocks:
                    if block[4].strip():
                        cleaned = self._clean_control_chars(block[4])
                        text_to_parse += cleaned
        return text_to_parse

    def _clean_control_chars(self, text: str) -> str:
        """Remove unwanted control characters."""
        control_chars = "".join(chr(i) for i in range(32)) + "".join(chr(i) for i in range(127, 160))
        translator = str.maketrans("", "", control_chars.replace("\n", "").replace("\t", ""))
        return text.translate(translator)

    def _extract_figure_descriptions(self, text: str) -> list[str]:
        """Extract figure descriptions from the text."""
        figure_descriptions = []
        description_matches = re.finditer(self.pattern_figure_descriptions, text, re.DOTALL | re.IGNORECASE)
        for description_match in description_matches:
            description = description_match.group(0).strip()
            figure_descriptions.append(description)
        return figure_descriptions

    def _extract_figures(self, pdf: PDF) -> list[str]:
        """Extract figures from the PDF and save them to the output directory."""
        output_dir = Path(self.figures_output_dir) / Path(pdf.path).stem
        output_dir.mkdir(parents=True, exist_ok=True)
        with pymupdf.open(pdf.path) as doc:
            figure_count = 0
            for page in doc:
                figures_list = page.get_images()
                for _fig_index, fig in enumerate(figures_list):
                    xref = fig[0]
                    base_figure = doc.extract_image(xref)
                    figure_bytes = base_figure["image"]
                    if self._figure_large_enough(figure_bytes):
                        self._save_figure(output_dir, figure_count, base_figure, figure_bytes)
                        figure_count += 1
                    else:
                        continue
            return [str(p) for p in sorted(output_dir.iterdir()) if p.is_file()]

    def _save_figure(self, output_dir: str, figure_count: int, base_figure: dict, figure_bytes: bytes) -> None:
        """Save the extracted figure to the output directory."""
        image_ext = base_figure["ext"]
        image_filename = output_dir / f"figure{figure_count + 1}.{image_ext}"
        with Path.open(image_filename, "wb") as img_file:
            img_file.write(figure_bytes)

    def _figure_large_enough(self, figure_bytes: bytes) -> bool:
        """Check if the figure is larger than 10 KB."""
        return len(figure_bytes) > 10 * 1024
