from __future__ import annotations
import base64
import json
import os
from itertools import product
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from aoptk.abbreviations.abbreviation_translator import AbbreviationTranslator
from aoptk.chemical import Chemical
from aoptk.effect import Effect
from aoptk.find_chemical import FindChemical
from aoptk.normalization.normalize_chemical import NormalizeChemical
from aoptk.relationship_type import Causative
from aoptk.relationship_type import Inhibitive
from aoptk.relationship_type import RelationshipType
from aoptk.relationships.find_relationship import FindRelationships
from aoptk.relationships.relationship import Relationship

topics = {Inhibitive(), Causative()}


class TextGenerationAPI(FindChemical, FindRelationships, AbbreviationTranslator, NormalizeChemical):
    """Text generation API using OpenAI."""

    role: str = "user"
    temperature: float = 0
    top_p: float = 1
    load_dotenv()
    client: None = None
    max_images_per_batch: int = 5

    relationship_text_prompt: str = """
    Task:
    Given the Context, determine whether the chemical {chem} {rel_type.positive_verb} the biological effect {effect}.

    Effect synonyms:
    - Treat common synonyms or equivalent terms as the same effect.
    - Always map any synonym in the Context to the target effect before evaluating.

    Decision rules:
    - Return {rel_type.positive} if the Context explicitly states that {chem} {rel_type.positive_verb} {effect}.
    - Return {rel_type.negative} if the Context explicitly states that {chem} {rel_type.negative_verb} {effect}.
    - Return "none" if:
        - The chemical or the effect is not mentioned, or
        - No direct relationship is stated, or
        - The statement is speculative, conditional, or indirect (e.g., uses "may", "might", "could").
    - VERY IMPORTANT: In all other cases: {other_topics} relationships - return "none".

    Output:
    Return exactly one of the following, with no extra text:
    {rel_type.positive}
    {rel_type.negative}
    none

    Context:
    {text}
    """

    relationship_text_images_prompt: str = """
    Task:
    Analyze the provided Context and Images.

    Step 1 — Chemical Extraction:
    - Identify all chemical entities (chemicals or metabolites).
    - Replace abbreviations with full chemical names.
    - Always write chemical names in lowercase.
    - Do NOT modify or expand chemical formulas (e.g., NaCl must remain exactly as written).
    - Do NOT treat broad classes (e.g., pesticides, proteins, plastics) as individual chemicals.

    Step 2 — Relationship Evaluation:
    Determine whether each chemical {rel_type.positive_verb} the biological effect "{effect}".
    Treat synonyms of the effect as equivalent.

    Output Rules:
    - Only output chemicals with a clear positive or negative relationship.
    - Exclude chemicals with no clear relationship.
    - If none qualify, output exactly:
    none

    Format:
    full_chemical_name_in_lowercase : relationship

    Where relationship must be exactly:
    {rel_type.positive}
    {rel_type.negative}

    Strict:
    - Chemical names must be full names and lowercase.
    - No blank relationships.
    - No extra text.
    - One chemical per line.

    Context:
    {text}
    """

    relationship_additional_prompt: str = """
    Rules:
    1. Use ONLY the information explicitly stated in the Context.
    2. Do NOT use biological knowledge, assumptions, or inferred relationships.
    3. Do NOT assume causal chains or indirect effects.
    """

    chemical_prompt: str = """
    Task:
    Extract chemical entities (e.g., chemicals, metabolites) from the provided Context.
    Replace all chemical abbreviations with their full chemical names.
    Do not modify, interpret, or expand chemical formulas (e.g., NaCl); keep them exactly as written.
    Refrain from describing groups of chemicals as discrete chemical entities (e.g., pesticides, plastics, proteins).


    Output requirements:
    1. Return only chemical names.
    2. Do not include explanations, labels, or any additional text.
    3. Separate chemical names exactly with " ; " (space-semicolon-space).
    4. Do not add leading or trailing separators.
    5. Do not include running characters` such as " - " (space-dash-space) or ": - " (colon-space-dash-space)
    in chemical names.
    6. If no chemical entities are present, return an empty string.

    Context:
    {text}
    """

    abbreviation_prompt: str = """
    You are expanding abbreviations in scientific and biomedical text.

    TASK:
    Rewrite the input text by replacing abbreviations with their full forms.

    SCOPE:
    - Expand ONLY:
    1) Chemical entities (chemicals, compounds, pollutants)
    2) Biological effects or processes (e.g., cell activation, toxicity,
    fibrosis-related events)
    - Do NOT expand:
    - Cell lines, cell types names used as labels (e.g., HepaRG, THP-1)
    - Genes or proteins unless they describe an effect
    - Assays, methods, or analysis names (e.g., RHT)

    RULES (in priority order):

    1. CONTEXT FIRST (MANDATORY):
    - If an abbreviation is explicitly defined in the text
        (e.g., "thioacetamide (TAA)", "benzo[a]pyrene (BaP)",
        "hepatic stellate cell (HSC) activation"),
        you MUST use that definition.
    - Treat the abbreviation and full form as equivalent.

    2. SCIENTIFIC STANDARD INFERENCE (FALLBACK):
    - If an abbreviation is NOT defined in the text,
        expand it ONLY if it has a widely accepted, unambiguous meaning
        in scientific or biomedical literature.
    - Examples of acceptable inference:
        - HSC activation → hepatic stellate cell activation
        - ECM remodeling → extracellular matrix remodeling
    - If the expansion is uncertain or ambiguous, leave it unchanged.

    3. CONSISTENCY:
    - Once an abbreviation is expanded, use the full form consistently
        throughout the text.
    - Do NOT reintroduce the abbreviation.

    4. GRAMMAR:
    - Preserve the original meaning, tense, and sentence structure.
    - Only modify the expanded terms.

    5. CAPITALIZATION:
    - If an abbreviation appears at the start of a sentence, capitalize the
    first letter of its expansion.
    - Example: "TAA was studied..." → "Thioacetamide was studied..."
    - Otherwise, preserve the original capitalization style of the
    surrounding text.

    6. CHARACTER ENCODING:
    - Use ONLY standard ASCII punctuation characters.
    - Use regular hyphens (-) NOT Unicode non-breaking hyphens (‑).
    - Use regular apostrophes (') NOT Unicode prime symbols (′).

    7. FORMATTING RULES:
    - When expanding abbreviations in lists, maintain the original
    parentheses structure.
    - Example: "chemicals (A, B and C)" → "chemicals (expanded-A, expanded-B
    and expanded-C)"
    - Do NOT change parentheses to commas or other punctuation.
    - Preserve all original punctuation except the abbreviations being
    expanded.

    OUTPUT:
    - Return ONLY the rewritten text.
    - Do NOT add explanations, comments, or formatting.

    INPUT TEXT:
    {text}
    """

    relationships_image_prompt: str = """
    Analyze this scientific graph for the biological effect {effect}.
    CRITICAL: Use ONLY what is explicitly visible. Zero tolerance for inference, assumptions, or interpretation.

    Output format:
    full_chemicalname_in_lowercase : relationship

    Extraction rules:
    - Extract ONLY individual chemicals explicitly named in the figure
    - Expand abbreviations to full chemical names (e.g., TAA → thioacetamide)
    - Exclude: abbreviations, chemical classes, mixtures, groups, vague terms
    - Do not include running characters

    Relationship rules:
    - {rel_type.positive} = graph clearly shows chemical {rel_type.positive_verb} {effect}
    - {rel_type.negative} = graph clearly shows chemical {rel_type.negative_verb} {effect}
    - Include ONLY if 100% certain and visually unambiguous
    - If significance, trend, or relationship requires ANY interpretation → EXCLUDE

    STRICT: When in doubt, exclude.

    If no chemicals qualify, output:
    none
    """

    relationships_table_prompt: str = """
    You are an assistant analyzing data from tables related to the biological effect {effect}.
    Your task is to process the provided information and output the results in this strict format, one per line:

    Format:
    full_chemical_name_in_lowercase : relationship

    Guidelines:
    1. Replace "full_chemical_name_in_lowercase" with the translated full name of the chemical (all lowercase).
    2. Replace "relationship" with:
    - {rel_type.positive} if the chemical {rel_type.positive_verb} {effect}.
    - {rel_type.negative} if the chemical {rel_type.negative_verb} {effect}.
    3. No headers, explanations, or extra text may be included in the output.
    4. Respond only with lines matching the format above—each line must correspond to a single chemical and its
    relationship.
    5. Handle incomplete or unrelated data as follows:
    - If only partial data is given (e.g., some chemicals mentioned but not all effects), include only the chemicals
    with identifiable effects.
    - If no relevant data (chemicals or {effect} effects) is provided, output "none".

    Table:
    {table}
    """

    normalization_prompt: str = """
    You are a chemical name normalization assistant.

    Task:
    You will be given:
    - A TARGET chemical name: {chem}
    - A LIST OF CHEMICAL NAMES (one chemical name per line)

    Your job is to:
    1. Determine whether {chem} matches any chemical in the list.
    2. Matching should include:
    - Synonyms (e.g., paracetamol = acetaminophen)
    - Abbreviations (e.g., PCB = polychlorinated biphenyl)
    - Alternate spellings, hyphenation, or formatting differences
    - Plural vs singular forms
    3. If multiple matches exist, return the most likely standardized match based on common chemical naming conventions.
    4. If there is no match, return: "none".

    Output rules:
    - Return only the matched chemical name from the list.
    - Do not explain.
    - Do not return anything except the answer.
    - If no match is found, return exactly "none".

    TARGET: {chem}

    LIST OF CHEMICAL NAMES:
    {list_of_chemical_names}
    """

    extract_text_from_image_prompt: str = """
    Extract the complete text from the provided scientific paper image, preserving all original line breaks, spacing,
    and paragraph structure exactly as shown.
    Output only the extracted text with no additional commentary or formatting, and ensure that no
    extra spaces are inserted between letters or words.
    """

    normalization_mapping_prompt = """
    You are a chemical name normalization assistant.

    Task:
    You will be given:
    1. A LIST OF TARGET CHEMICAL NAMES
    2. A REFERENCE LIST OF STANDARD CHEMICAL NAMES

    For EACH target chemical:
    - Determine whether it matches a chemical in the reference list.

    Matching rules:
    - Same chemical names should be considered a match
    - Synonyms
    - Abbreviations
    - Alternate spellings or hyphenation
    - Formatting differences
    - Singular vs plural
    - Common vs systematic names

    Output format rules:
    - Return a JSON dictionary
    - Keys = original target names
    - Values = matched reference name OR "none"
    - Do NOT include explanations
    - Do NOT include any text outside JSON

    TARGET LIST:
    {target_list}

    REFERENCE LIST:
    {reference_list}
    """
    image_to_text_prompt = """
    Describe what is shown in this image from a scientific paper.

    If the image appears to be a scan of a scientific paper page, return an empty string.
    """

    def __init__(
        self,
        model: str = "gpt-oss-120b",
        url: str = "https://llm.ai.e-infra.cz/v1",
        api_key: str = os.getenv("CERIT_API_KEY"),
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
            if (response := self._prompt_text(text, chemical, effect, relationship_type)) and (
                relationship := self._select_relationship_type(response, relationship_type)
            ):
                relationships.append(
                    Relationship(relationship_type=relationship, chemical=chemical, effect=effect, context=text),
                )
        return relationships

    def _prompt_text(self, text: str, chemical: Chemical, effect: Effect, relationship_type: RelationshipType) -> str:
        """Classify the relationship between a chemical and an effect.

        Args:
            text (str): The input text.
            chemical (Chemical): The chemical entity.
            effect (Effect): The effect entity.
            relationship_type (RelationshipType): The relationship type to classify.
        """
        other_topics = topics.difference({relationship_type})
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            top_p=self.top_p,
            messages=[
                {
                    "role": self.role,
                    "content": self.relationship_text_prompt.format(
                        text=text,
                        chem=chemical.name,
                        effect=effect.name,
                        rel_type=relationship_type,
                        other_topics=", ".join([topic.positive for topic in other_topics]),
                    ),
                },
            ],
        )
        return completion.choices[0].message.content.strip().lower()

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

    def find_chemical(self, text: str) -> list[Chemical]:
        """Find chemicals in the given text.

        Args:
            text (str): The input text to search for chemicals.
        """
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            top_p=self.top_p,
            messages=[
                {
                    "role": self.role,
                    "content": self.chemical_prompt.format(text=text),
                },
            ],
        )
        response = completion.choices[0].message.content
        if response is None:
            return []
        return [Chemical(name=chem.strip().lower()) for chem in response.split(" ; ")] if response.strip() else []

    def translate_abbreviation(self, text: str) -> str:
        """Translate abbreviations in the given text to their full forms.

        Args:
            text (str): The input text containing abbreviations.
        """
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            top_p=self.top_p,
            messages=[
                {
                    "role": self.role,
                    "content": self.abbreviation_prompt.format(text=text),
                },
            ],
        )
        response = completion.choices[0].message.content
        return response if response is not None else text

    def find_relationships_in_image(
        self,
        image_path: str,
        relationship_type: RelationshipType,
        effects: list[Effect],
    ) -> list[Relationship]:
        """Find relationships between chemicals and effects in an image.

        Args:
            image_path (str): Path to the image.
            relationship_type (RelationshipType): The relationship type to classify.
            effects (list[Effect]): List of effect entities.
        """
        relationships = []
        for effect in effects:
            relationships.extend(self._classify_relationships_in_image(image_path, effect, relationship_type))
        return relationships

    def _classify_relationships_in_image(
        self,
        image_path: str,
        effect: Effect,
        relationship_type: RelationshipType,
    ) -> list[Relationship]:
        """Classify relationships between chemicals and an effect in an image.

        Args:
            image_path (str): Path to the image.
            effect (Effect): The effect entity.
            relationship_type (RelationshipType): The relationship type to classify.

        Returns:
            list[Relationship]: List of relationships found in the image.
        """
        base64_image, mime_type = self._encode_image(image_path)

        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            top_p=self.top_p,
            messages=[
                {
                    "role": self.role,
                    "content": [
                        {
                            "type": "text",
                            "text": self.relationships_image_prompt.format(
                                effect=effect.name,
                                rel_type=relationship_type,
                            ),
                        },
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}},
                    ],
                },
            ],
        )
        if (content := completion.choices[0].message.content) and (response := content.strip().lower()):
            return self._process_colon_separated_response(
                response,
                effect,
                relationship_type,
                image_path,
            )
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
        relationship_type: RelationshipType,
        effects: list[Effect],
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

        messages = [
            {
                "role": self.role,
                "content": self.relationships_table_prompt.format(
                    effect=effect.name,
                    rel_type=relationship_type,
                    table=table_text,
                ),
            },
        ]

        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            top_p=self.top_p,
            messages=messages,
        )
        if (content := completion.choices[0].message.content) and (response := content.strip().lower()):
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

    def _find_matching_name(self, chemical: Chemical, chemical_list: list[Chemical]) -> Chemical:
        """Find a matching chemical name in the chemical list.

        Args:
            chemical (Chemical): The chemical to find a match for.
            chemical_list (list[Chemical]): The list of chemicals to match against.

        Returns:
            Chemical: The matching chemical name, or None if no match is found.
        """
        messages = [
            {
                "role": self.role,
                "content": self.normalization_prompt.format(
                    chem=chemical.name,
                    list_of_chemical_names="\n".join([chem.name for chem in chemical_list]),
                ),
            },
        ]

        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            top_p=self.top_p,
            messages=messages,
        )
        if response := completion.choices[0].message.content.strip().lower():
            if response == "none":
                return None
            return response
        return None

    def extract_text_from_pdf_image(
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
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            top_p=self.top_p,
            messages=[
                {
                    "role": self.role,
                    "content": [
                        {
                            "type": "text",
                            "text": self.extract_text_from_image_prompt,
                        },
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{img_base64.strip()}"}},
                    ],
                },
            ],
        )
        if (content := completion.choices[0].message.content) and (response := content.strip()):
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
        all_relationships = []
        other_topics = topics.difference({relationship_type})

        for i in range(0, len(image_paths), self.max_images_per_batch):
            batch_image_paths = image_paths[i : i + self.max_images_per_batch]
            encoded_images = [self._encode_image(image_path) for image_path in batch_image_paths]

            content = [
                {
                    "type": "text",
                    "text": self.relationship_text_images_prompt.format(
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

            completion = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                top_p=self.top_p,
                messages=[{"role": self.role, "content": content}],
            )

            if (content := completion.choices[0].message.content) and (response := content.strip().lower()):
                all_relationships.extend(
                    self._process_colon_separated_response(
                        response,
                        effect,
                        relationship_type,
                        "text and images",
                    ),
                )

        return all_relationships

    def generate_normalization_mapping(
        self,
        target_chemicals: list[Chemical],
        reference_chemicals: set[Chemical],
    ) -> dict[str, str]:
        """Return a mapping of target names to reference names that can be used for a dataframe.

        Args:
            target_chemicals (list[Chemical]): Chemicals to normalize.
            reference_chemicals (set[Chemical]): Reference chemicals to match against.

        Returns:
            dict[str, str]: Mapping of target names to matched reference names or "none".
        """
        target_list = "\n".join(chem.name for chem in target_chemicals)
        reference_list = "\n".join(chem.name for chem in reference_chemicals)

        messages = [
            {
                "role": self.role,
                "content": self.normalization_mapping_prompt.format(
                    target_list=target_list,
                    reference_list=reference_list,
                ),
            },
        ]

        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            top_p=self.top_p,
            messages=messages,
        )

        if (content := completion.choices[0].message.content) and (response := content.strip().lower()):
            mapping = json.loads(response)
            return {str(key).strip().lower(): str(value).strip().lower() for key, value in mapping.items()}
        return {}

    def convert_image_to_text(
        self,
        image_path: str,
    ) -> str:
        """Convert an image to text.

        Args:
            image_path (str): Path to the image.
        """
        base64_image, mime_type = self._encode_image(image_path)

        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            top_p=self.top_p,
            messages=[
                {
                    "role": self.role,
                    "content": [
                        {
                            "type": "text",
                            "text": self.image_to_text_prompt,
                        },
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}},
                    ],
                },
            ],
        )
        if (content := completion.choices[0].message.content) and (response := content.strip().lower()):
            return response
        return ""
