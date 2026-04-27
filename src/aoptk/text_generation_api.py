from __future__ import annotations
import base64
import os
from itertools import product
from pathlib import Path
import pandas as pd
from Cheetah.Template import Template
from dotenv import load_dotenv
from openai import OpenAI
from aoptk.chemical import Chemical
from aoptk.effect import Effect
from aoptk.find_chemical import FindChemical
from aoptk.literature.convert_image import ConvertImage
from aoptk.literature.convert_pdf_scan import ConvertPDFScan
from aoptk.literature.find_relevant_publication import FindRelevantPublication
from aoptk.normalization.normalize_chemical import NormalizeChemical
from aoptk.relationship_type import Causative
from aoptk.relationship_type import Inhibitive
from aoptk.relationship_type import RelationshipType
from aoptk.relationships.find_relationship import FindRelationship
from aoptk.relationships.relationship import Relationship

topics = {Inhibitive(), Causative()}


class LLMFailureError(Exception):
    """Base class for capturing LLM failures."""

    def __init__(self):
        pass


class TextGenerationAPI(
    FindChemical,
    FindRelationship,
    NormalizeChemical,
    ConvertPDFScan,
    ConvertImage,
    FindRelevantPublication,
):
    """Text generation API using OpenAI."""

    role: str = "user"
    temperature: float = 0
    top_p: float = 1
    load_dotenv()
    client: None = None
    prompts_dir: Path = Path(__file__).resolve().parent / "prompts"
    chemical_prompt_template: str = "chemical_prompt.txt"
    relationship_text_prompt_template: str = "relationship_text_prompt.txt"
    relationship_text_images_prompt_template: str = "relationship_text_images_prompt.txt"
    relationships_table_prompt_template: str = "relationships_table_prompt.txt"
    normalization_prompt_template: str = "normalization_prompt.txt"
    convert_pdf_scan_prompt_template: str = "convert_pdf_scan_prompt.txt"
    convert_image_prompt_template: str = "convert_image_prompt.txt"
    find_relevant_publications_prompt_template: str = "find_relevant_publications_prompt.txt"

    specification_relationship_text_prompt: str = ""

    def __init__(
        self,
        model: str = "gpt-oss-120b",
        url: str = "https://llm.ai.e-infra.cz/v1",
        api_key: str = os.environ.get("CERIT_API_KEY"),
    ):
        self.model = model
        self.url = url
        self.api_key = api_key
        if self.client is None:
            self.client = OpenAI(
                base_url=self.url,
                api_key=self.api_key,
            )

    def find_relationships_in_text(
        self,
        text: str,
        chemicals: list[Chemical],
        effects: list[Effect],
        relationship_type: RelationshipType,
    ) -> list[Relationship]:
        """Find relationships between chemicals and effects.

        Args:
            text (str): The input text.
            chemicals (list[Chemical]): List of chemical entities.
            effects (list[Effect]): List of effect entities.
            relationship_type (RelationshipType): The relationship type to classify.
        """
        relationships = []
        for chemical, effect in product(chemicals, effects):
            if (response := self._relationship_prompt(text, chemical, effect, relationship_type)) and (
                relationship := self._select_relationship_type(response, relationship_type)
            ):
                relationships.append(
                    Relationship(relationship_type=relationship, chemical=chemical, effect=effect, context=text),
                )
        return relationships

    def _relationship_prompt(
        self,
        text: str,
        chemical: Chemical,
        effect: Effect,
        relationship_type: RelationshipType,
    ) -> str:
        """Classify the relationship between a chemical and an effect.

        Args:
            text (str): The input text.
            chemical (Chemical): The chemical entity.
            effect (Effect): The effect entity.
            relationship_type (RelationshipType): The relationship type to classify.
        """
        other_topics = topics.difference({relationship_type})
        content = self._render_prompt(
            self.relationship_text_prompt_template,
            text=text,
            chem=chemical.name,
            effect=effect.name,
            rel_type=relationship_type,
            other_topics=", ".join([topic.positive for topic in other_topics]),
            specification_relationship_text_prompt=self.specification_relationship_text_prompt,
        )

        return self._prompt(content)

    def _render_prompt(self, template_name: str, **context: object) -> str:
        template_path = self.prompts_dir / template_name
        with template_path.open(encoding="utf-8") as template_file:
            template_content = template_file.read()
        return str(Template(template_content, searchList=[context]))

    def _prompt(self, content: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            top_p=self.top_p,
            messages=[
                {
                    "role": self.role,
                    "content": content,
                },
            ],
        )

        if response := completion.choices[0].message.content:
            return response.strip()
        raise LLMFailureError

    def _select_relationship_type(self, response: str, relationship_type: RelationshipType) -> str | None:
        """Select the relationship type based on the response.

        Args:
            response (str): The response from the model indicating the relationship type.
            relationship_type (RelationshipType): The relationship type to classify.
        """
        if response == relationship_type.positive:
            return relationship_type.positive
        if response == relationship_type.negative:
            return relationship_type.negative
        return None

    def find_chemicals(self, text: str) -> list[Chemical]:
        """Find chemicals in the given text.

        Args:
            text (str): The input text to search for chemicals.
        """
        if response := self._prompt(self._render_prompt(self.chemical_prompt_template, text=text)).lower():
            if response == "none":
                return []
            return [Chemical(name=chem.strip().lower()) for chem in response.split(" ; ")] if response.strip() else []
        return []

    def _encode_image(self, image_path: str) -> tuple[str, str]:
        """Encode the image at the given path to a base64 string and return MIME type.

        Args:
            image_path (str): The path to the image to encode.

        Returns:
            tuple[str, str]: A tuple of (base64_encoded_image, mime_type).
        """
        ext = Path(image_path).suffix.lower()
        mime_type = f"image/{ext[1:]}"

        with Path(image_path).open("rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        return base64_image, mime_type

    def _process_colon_separated_response(
        self,
        response: str,
        effect: Effect,
        relationship_type: RelationshipType,
        image_path: str,
    ) -> list[Relationship]:
        """Process the response from the model that is colon seperated.

        Args:
            response (str): The response from the model.
            effect (Effect): The effect entity.
            relationship_type (RelationshipType): The relationship type to classify.
            context (str): The path to the image, used for context in the relationship.
            image_path (str): The path to the image, used for context in the relationship.
        """
        relationships = []
        for raw_line in response.splitlines():
            line = raw_line.strip()
            if " : " not in line:
                continue

            chem_name, classification = line.split(" : ", 1)
            chem_name = chem_name.strip().lower()
            classification = classification.strip().lower()

            relationship = self._select_relationship_type(classification, relationship_type)

            relationships.append(
                Relationship(
                    relationship_type=relationship,
                    chemical=Chemical(name=chem_name),
                    effect=effect,
                    context=Path(image_path).stem,
                ),
            )

        return relationships

    def find_relationships_in_table(
        self,
        table_df: pd.DataFrame,
        effects: list[Effect],
        relationship_type: RelationshipType,
    ) -> list[Relationship]:
        """Find relationships between chemicals and effects in a table.

        Args:
            table_df (pd.DataFrame): Pandas DataFrame.
            relationship_type (RelationshipType): The relationship type to classify.
            effects (list[Effect]): List of effect entities.
        """
        relationships = []
        for effect in effects:
            relationships.extend(
                self._classify_relationships_in_table(
                    table_df,
                    effect,
                    relationship_type,
                ),
            )
        return relationships

    def _classify_relationships_in_table(
        self,
        table_df: pd.DataFrame,
        effect: Effect,
        relationship_type: RelationshipType,
    ) -> list[Relationship]:
        """Classify relationships between chemicals and an effect in a table.

        Args:
            table_df (pd.DataFrame): Pandas DataFrame.
            effect (Effect): The effect entity.
            relationship_type (RelationshipType): The relationship type to classify.

        Returns:
            list[Relationship]: List of relationships found in the table.
        """
        table_text = table_df.to_csv(index=False)

        content = self._render_prompt(
            self.relationships_table_prompt_template,
            effect=effect.name,
            rel_type=relationship_type,
            table=table_text,
        )

        if response := self._prompt(content):
            return self._process_colon_separated_response(response, effect, relationship_type, "table")
        return []

    def normalize_chemical(self, chemical: Chemical, chemical_list: list[Chemical]) -> Chemical:
        """Normalize the chemical name by finding a matching name in the chemical list.

        Args:
            chemical (Chemical): The chemical to normalize.
            chemical_list (list[Chemical]): The list of chemicals to match against.

        Returns:
            Chemical: The normalized chemical.
        """
        if matching_name := self._find_matching_name(chemical, chemical_list):
            chemical.heading = matching_name
        return chemical

    def _find_matching_name(self, chemical: Chemical, chemical_list: list[Chemical]) -> Chemical | None:
        """Find a matching chemical name in the chemical list.

        Args:
            chemical (Chemical): The chemical to find a match for.
            chemical_list (list[Chemical]): The list of chemicals to match against.

        Returns:
            Chemical: The matching chemical name, or None if no match is found.
        """
        content = self._render_prompt(
            self.normalization_prompt_template,
            chem=chemical.name,
            list_of_chemical_names="\n".join([chem.name for chem in chemical_list]),
        )

        if response := self._prompt(content).lower():
            if response == "none":
                return chemical.name
            return response
        return chemical.name

    def convert_pdf_scan(
        self,
        img_base64: str,
        mime_type: str,
    ) -> str:
        """Extract text from a base64-encoded image.

        Args:
            img_base64 (str): Base64-encoded image data.
            mime_type (str): MIME type of the image. Defaults to "image/jpeg".

        Returns:
            str: Extracted text from the image.
        """
        content = [
            {
                "type": "text",
                "text": self._render_prompt(self.convert_pdf_scan_prompt_template),
            },
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{img_base64.strip()}"}},
        ]

        if response := self._prompt(content):
            return response
        return ""

    def find_relationships_in_text_and_images(
        self,
        text: str,
        image_paths: list[str],
        relationship_type: RelationshipType,
        effects: list[Effect],
    ) -> list[Relationship]:
        """Find relationships between chemicals and effects in the given text and images combined.

        Args:
            text (str): The input text.
            image_paths (list[str]): List of paths to images.
            relationship_type (RelationshipType): The relationship type to classify.
            effects (list[Effect]): List of effect entities.
        """
        relationships = []
        for effect in effects:
            relationships.extend(
                self._classify_relationships_in_text_and_images(text, image_paths, effect, relationship_type),
            )
        return relationships

    def _classify_relationships_in_text_and_images(
        self,
        text: str,
        image_paths: list[str],
        effect: Effect,
        relationship_type: RelationshipType,
    ) -> list[Relationship]:
        """Classify relationships between chemicals and an effect in the given text and images combined.

        Args:
            text (str): The input text.
            image_paths (list[str]): List of paths to images.
            effect (Effect): The effect entity.
            relationship_type (RelationshipType): The relationship type to classify.
        """
        other_topics = topics.difference({relationship_type})

        encoded_images = [self._encode_image(image_path) for image_path in image_paths]

        relationships = []

        content = [
            {
                "type": "text",
                "text": self._render_prompt(
                    self.relationship_text_images_prompt_template,
                    text=text,
                    effect=effect.name,
                    rel_type=relationship_type,
                    other_topics=", ".join([topic.positive for topic in other_topics]),
                ),
            },
        ]

        content.extend(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{img}"},
            }
            for img, mime_type in encoded_images
        )

        response = self._prompt(content)

        if response:
            relationships.extend(
                self._process_colon_separated_response(
                    response,
                    effect,
                    relationship_type,
                    "text and images",
                ),
            )
        return relationships

    def convert_image(
        self,
        image_path: str,
        text: str,
    ) -> str:
        """Convert an image to text.

        Args:
            image_path (str): Path to the image.
            text (str): The full text of the publication for context.
        """
        base64_image, mime_type = self._encode_image(image_path)

        content = [
            {
                "type": "text",
                "text": self._render_prompt(self.convert_image_prompt_template, text=text),
            },
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}},
        ]

        if response := self._prompt(content):
            return response
        return ""

    def find_relevant_publications(self, question: str, text: str) -> bool | None:
        """Answer the question based on a given text.

        Args:
            question (str): The question to search for relevant publications.
            text (str): The extracted text of the publication.
        """
        if response := self._prompt(
            self._render_prompt(self.find_relevant_publications_prompt_template, question=question, text=text),
        ).lower():
            if response == "yes":
                return True
            if response == "no":
                return False
        return None
