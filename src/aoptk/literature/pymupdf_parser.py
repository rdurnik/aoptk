from __future__ import annotations
import base64
import re
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Self
import pymupdf
from aoptk.inject_text_generation import TextGenerationInjector
from aoptk.literature.abstract import Abstract
from aoptk.literature.id import ID
from aoptk.literature.pdf import PDF
from aoptk.literature.pdf_parser import PDFParser
from aoptk.literature.publication import Publication

if TYPE_CHECKING:
    from aoptk.literature.pdf import PDF
    from aoptk.text_generation_api import TextGenerationAPI


class PymupdfParser(PDFParser, TextGenerationInjector):
    """Parse PDFs using PyMuPDF."""

    def __init__(self, pdfs: list[PDF], figure_storage: str = "tests/figure_storage"):
        self.figure_storage = figure_storage
        self.pdfs = pdfs
        self.pattern_figure_descriptions = r"(?ms)(?<=\n)\s*Figure\s+\d+\.?\s*(.*?)(?=\n)"
        self.pattern_any_character = r"(.*)"
        self.text_generation = None

    def inject_text_generation(self, text_generation: TextGenerationAPI) -> Self:
        """Inject text generation dependency (voluntary).

        Args:
            text_generation (TextGenerationAPI): The text generation API to use for converting PDF scans to text.
        """
        self.text_generation = text_generation
        return self

    def get_publications(self) -> list[Publication]:
        """Get a list of publications."""
        pubs = []
        for pdf in self.pdfs:
            pub = self._parse_pdf(pdf)
            pubs.append(pub)
        return pubs

    def get_abstracts(self) -> list[Abstract]:
        """Get abstracts from the PDFs.

        Returns:
            list[Abstract]: List of abstracts obtained from the PDF's.
        """
        abstracts = []
        for pdf in self.pdfs:
            publication_id = ID(Path(pdf.path).stem)
            abstract = self._extract_abstract(pdf, publication_id)
            abstracts.append(abstract)
        return abstracts

    def _parse_pdf(self, pdf: PDF) -> Publication:
        """Parse a single PDF and return a Publication object."""
        text_to_parse = self._extract_text_to_parse(pdf)
        publication_id = ID(Path(pdf.path).stem)
        abstract = self._extract_abstract(pdf, publication_id)
        full_text = self._extract_full_text(pdf)
        figures = self._extract_figures(pdf)
        figure_descriptions = self._extract_figure_descriptions(text_to_parse)
        tables = []
        return Publication(
            id=publication_id,
            abstract=abstract,
            full_text=full_text,
            figures=figures,
            figure_descriptions=figure_descriptions,
            tables=tables,
        )

    def _extract_abstract(self, pdf: PDF, publication_id: ID) -> Abstract:
        """Extract the abstract from the text."""
        with pymupdf.open(pdf.path) as doc:
            page = doc[0]
            if text_blocks := self._extract_text_blocks_without_irrelevant_border_text(
                pages=((0, page),),
            ):
                longest_block = max(text_blocks, key=lambda b: len(b[6]))
                abstract_text = "\n".join(block[6] for block in text_blocks if block == longest_block)
            else:
                abstract_text = ""
        return Abstract(abstract_text, publication_id)

    def _extract_full_text(self, pdf: PDF) -> str:
        """Extract text to parse from the PDF.

        Args:
            pdf (PDF): The PDF object to extract text from.

        Returns:
            str: The extracted full text from the PDF.
        """
        with pymupdf.open(pdf.path) as doc:
            text_blocks = self._extract_text_blocks_without_irrelevant_border_text(
                pages=enumerate(doc, start=0),
            )
            full_text = "\n".join(block[6] for block in text_blocks)
            if (self._is_corrupted(full_text) or self._is_too_short(full_text)) and self.text_generation:
                pdf_as_images = self._extract_pdf_as_images(pdf)
                full_text = self._extract_full_text_from_images(pdf_as_images)

            return full_text

    def _is_too_short(self, text: str, min_length: int = 1000) -> bool:
        """Check if the text is too short to be a valid full text.

        Args:
            text (str): The text to check.
            min_length (int): The minimum length of valid full text.

        Returns:
            bool: True if the text is too short, False otherwise.
        """
        return len(text.strip()) < min_length

    def _is_corrupted(self, text: str, max_corruption_ratio: float = 0.1) -> bool:
        """Check if the text is corrupted based on the ratio of control characters.

        Args:
            text (str): The text to check.
            max_corruption_ratio (float): The maximum allowed ratio of corrupted characters.

        Returns:
            bool: True if the text is corrupted, False otherwise.
        """
        if not text:
            return False
        corrupted_text = len(re.findall(r"(?:[\x00-\x1F\x7F]|\uFFFD|/C\d{2,3})", text))
        corruption_ratio = corrupted_text / len(text)
        return corruption_ratio > max_corruption_ratio

    def _extract_pdf_as_images(self, pdf: PDF) -> list[str]:
        """Extract each page of the PDF as an image and return a list of base64-encoded images.

        Args:
            pdf (PDF): The PDF object to extract images from.

        Returns:
            list[str]: A list of base64-encoded image strings.
        """
        pdf_document = pymupdf.open(pdf.path)
        images_base64 = []

        with pymupdf.open(pdf.path) as doc:
            for page in doc:
                matrix = pymupdf.Matrix(2, 2)
                pixmap = page.get_pixmap(matrix=matrix, alpha=False)
                png_bytes = pixmap.tobytes("png")
                img_base64 = base64.b64encode(png_bytes).decode("utf-8")
                images_base64.append(img_base64)
        pdf_document.close()
        return images_base64

    def _extract_full_text_from_images(self, pdf_as_images: list[str]) -> str:
        """Extract text from a list of base64-encoded images using the TextGenerationAPI.

        Args:
            pdf_as_images (list[str]): A list of base64-encoded image strings.

        Returns:
            str: The extracted full text from the images.
        """
        full_text = ""
        for img_base64 in pdf_as_images:
            text_from_image = self.text_generation.convert_pdf_scan(img_base64, mime_type="image/png")
            full_text += text_from_image + "\n"
        return full_text

    def _extract_text_blocks_without_irrelevant_border_text(
        self,
        pages: Iterable[tuple[int, pymupdf.Page]],
        top_margin_frac: float = 0.07,
        bottom_margin_frac: float = 0.07,
        side_margin_frac: float = 0.02,
    ) -> list[tuple[int, int, float, float, float, float, str]]:
        """Collect text blocks from pages within margin bounds."""
        text_blocks = []
        for page_index, page in pages:
            page_layout = page.rect
            x0_min = page_layout.x0 + page_layout.width * side_margin_frac
            x1_max = page_layout.x1 - page_layout.width * side_margin_frac
            y0_min = page_layout.y0 + page_layout.height * top_margin_frac
            y1_max = page_layout.y1 - page_layout.height * bottom_margin_frac

            blocks = page.get_text("blocks")
            for block in blocks:
                x0, y0, x1, y1, text, block_no, _block_type = block
                text = text.strip()
                if not text:
                    continue
                if x0 < x0_min or x1 > x1_max or y0 < y0_min or y1 > y1_max:
                    continue
                text_blocks.append((page_index, block_no, x0, y0, x1, y1, text))

        text_blocks.sort(key=lambda b: (b[0], b[3], b[2]))
        return text_blocks

    def _extract_text_to_parse(self, pdf: PDF) -> str:
        """Extract text to parse from the PDF."""
        text_to_parse = ""
        with pymupdf.open(pdf.path) as doc:
            for page in doc:
                blocks = page.get_text("blocks")
                text_to_parse += "\n".join([" ".join(block[4].split()) for block in blocks if block[4].strip()])
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
        output_dir = Path(self.figure_storage) / Path(pdf.path).stem
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
        """Check if the figure is larger than 50 KB."""
        return len(figure_bytes) > 50 * 1024
