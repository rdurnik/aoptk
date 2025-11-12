import re
from pathlib import Path
import pymupdf
from aoptk.get_publication import GetPublication


class ParsePDF(GetPublication):
    def __init__(self, pdf: str):
        self.pdf = pdf

    def get_publication(self):
        return ""

    def parse_abstract(self):
        self.text_to_parse = self.extract_text_to_parse()
        match = self.extract_abstract_match_abstract_specified()
        if match:
            abstract = match.group(1).strip()
            return abstract
        if not match:
            match = self.extract_abstract_match_abstract_not_specified()
            if match:
                # This is not working perfectly.
                match = self.remove_title_authors(match)
                abstract = match.group(1).strip()
                return abstract
            match = self.extract_first_large_paragraph()
            if match:
                abstract = match.group().strip()
                return abstract

    def parse_full_text(self):
        self.text_to_parse = self.extract_text_to_parse()
        match = self.extract_abstract_match_abstract_specified()
        if match:
            match_end = match.end()
            full_text = self.text_to_parse[match_end:].strip()
            return full_text
        if not match:
            match = self.extract_abstract_match_abstract_not_specified()
            if match:
                match = self.remove_title_authors(match)
                match_end = match.end() + self.text_to_parse.index(match.group(0))
                full_text = self.text_to_parse[match_end:].strip()
                return full_text
            match = self.extract_first_large_paragraph()
            if match:
                match_end = match.end() + self.text_to_parse.index(match.group(0))
                full_text = self.text_to_parse[match_end:].strip()
                return full_text

    def extract_abstract_match_abstract_specified(self):
        pattern_abstract_written = r"(?i)a\s*b\s*s\s*t\s*r\s*a\s*c\s*t\s*[:\-]?\s*(.*?)\s*(?=\n\s*(?:keywords|introduction|1\.?\s|I\.)\b)"
        match = re.search(pattern_abstract_written, self.text_to_parse, re.DOTALL)
        if match:
            return match
        return None

    def extract_abstract_match_abstract_not_specified(self):
        pattern_abstract_not_written = r"(?:^|\n)((?:(?!\n\s*(?:keywords?|introduction|(?:1|I)\.?\s|section\s+1)\b).)*?)\s*(?=\n\s*(?:keywords?|introduction|(?:1|I)\.?\s|section\s+1)\b)"
        match = re.search(pattern_abstract_not_written, self.text_to_parse, re.DOTALL | re.IGNORECASE)
        if match:
            return match
        return None

    def remove_title_authors(self, match, newlines_to_remove_from_start = 2):
        text = match.group(1)
        parts = text.split("\n", newlines_to_remove_from_start)
        if len(parts) > newlines_to_remove_from_start:
            match = re.match(r"(.*)", parts[newlines_to_remove_from_start], re.DOTALL)
            return match

    def extract_first_large_paragraph(self, large_paragraph_word_count = 100):
        paragraphs = self.text_to_parse.split("\n")
        large_paragraphs = [p for p in paragraphs if len(p.split()) > large_paragraph_word_count]
        if large_paragraphs:
            first_large_paragraph = re.match(r"(.*)", large_paragraphs[0], re.DOTALL)
            return first_large_paragraph
        return None

    def extract_text_to_parse(self):
        text_to_parse = ""
        with pymupdf.open(self.pdf) as doc:
            for page in doc:
                blocks = page.get_text("blocks")
                text_to_parse += "\n".join([" ".join(block[4].split()) for block in blocks if block[4].strip()])
        return text_to_parse

    def extract_abbreviations(self):
        self.text_to_parse = self.extract_text_to_parse()
        pattern_abbreviations = r"(?i)Abbreviations[:\s]+(.*?)\."
        match = re.search(pattern_abbreviations, self.text_to_parse, re.DOTALL)
        abbreviations_dict = {}
        if match:
            abbreviation_text = match.group(1)
            abbreviation_text_without_new_lines = re.sub(r"\n+", " ", abbreviation_text)
            entries = re.split(r";\s*", abbreviation_text_without_new_lines.strip())
            for entry in entries:
                m = re.match(r"([A-Za-z0-9\-α-ωΑ-Ω]+)\s*[:,]\s*(.+)", entry.strip())
                if m:
                    key, value = m.groups()
                    abbreviations_dict[key.strip()] = value.strip()
        return abbreviations_dict

    def extract_figures(self, output_dir="/home/rdurnik/aoptk/tests/figure_storage"):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_document = pymupdf.open(self.pdf)
        image_count = 0
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_filename = output_dir / f"page{page_num + 1}_figure{img_index + 1}.{image_ext}"
                with open(image_filename, "wb") as img_file:
                    img_file.write(image_bytes)
                image_count += 1
        pdf_document.close()

    def extract_figure_descriptions(self, output_dir="/home/rdurnik/aoptk/tests/figure_storage"):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_document = pymupdf.open(self.pdf)
        caption_number = 0
        figure_descriptions = []
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            blocks = page.get_text("blocks")
            page_text = "\n".join([block[4] for block in blocks if block[6] == 0])
            figure_description_pattern = r"(?mi)^\s*Figure\s+\d+\.\s*(?:[^\n]*(?:\n(?!\s*\n)[^\n]*)*)"
            caption_match = re.search(figure_description_pattern, page_text, re.IGNORECASE)
            if caption_match:
                caption_number += 1
                caption = caption_match.group(0).strip()
                figure_descriptions.append(caption)
            else:
                continue
        pdf_document.close()
        return figure_descriptions
