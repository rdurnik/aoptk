from __future__ import annotations
import base64
import os
from itertools import product
from pathlib import Path
from typing import ClassVar
from dotenv import load_dotenv
from openai import OpenAI
from aoptk.abbreviations.abbreviation_translator import AbbreviationTranslator
from aoptk.chemical import Chemical
from aoptk.effect import Effect
from aoptk.relationship_type import Evidence, RelationshipType
from aoptk.find_chemical import FindChemical
from aoptk.relationships.find_relationship import FindRelationships
from aoptk.relationships.relationship import Relationship


class TextGenerationAPI(FindChemical, FindRelationships, AbbreviationTranslator):
    """Text generation API using OpenAI."""

    role: str = "user"
    temperature: float = 0
    top_p: float = 1
    load_dotenv()
    client: None = None

    relationship_types: ClassVar[dict[str, str | None]] = {
        "positive": "positive",
        "negative": "negative",
        "none": None,
        "inhibition": "inhibition",
        "no-inhibition": "no-inhibition",
    }

    relationship_prompt: str = """
                                Task:
                                Given the Context, determine whether the chemical {chemical} {relationship.positive_verb} the biological effect {effect}.

                                Effect synonyms:
                                - Treat common synonyms or equivalent terms as the same effect.
                                - Always map any synonym in the Context to the target effect before evaluating.

                                Decision rules:
                                - Return {relationship.positive} if the Context explicitly states that {chemical} {relationship.positive_verb} {effect}.
                                - Return {relationship.negative} if the Context explicitly states that {chemical} {relationship.negative_verb} {effect}.
                                - Return "none" if:
                                    - The chemical or the effect is not mentioned, or
                                    - No direct relationship is stated, or
                                    - The statement is speculative, conditional, or indirect (e.g., uses "may", "might", "could").
                                - VERY IMPORTANT: In all other cases ({other_topics}) return "none".

                                Output:
                                Return exactly one of the following, with no extra text:
                                {relationship.positive}
                                {relationship.negative}
                                none

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
                            Replace all chemical abbreviations with their full chemical names. Do not modify, interpret, or expand chemical formulas (e.g., NaCl); keep them exactly as written.
                            Refrain from describing groups of chemicals as discrete chemical entities (e.g., pesticides, plastics, proteins).


                            Output requirements:
                            1. Return only chemical names.
                            2. Do not include explanations, labels, or any additional text.
                            3. Separate chemical names exactly with " ; " (space-semicolon-space).
                            4. Do not add leading or trailing separators.
                            5. Do not include running characters` such as " - " (space-dash-space) or ": - " (colon-space-dash-space) in chemical names.
                            6. If no chemical entities are present, return an empty string.

                            Context:
                            {text}
                            """

    abbreviation_prompt: str = """You are expanding abbreviations in scientific and biomedical text.

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
                                        You are an assistant analyzing data from graphs or plots related to the biological effect {effect}.
                                        Your task is to process the provided information and output the results in this strict format, one per line:

                                        Format:
                                        full_chemical_name_in_lowercase : relationship

                                        Guidelines:
                                        1. Replace "full_chemical_name_in_lowercase" with the translated full name of the chemical (all lowercase).
                                        2. Replace "relationship" with:
                                        - {relationship_positive} if the chemical {relationship.positive_verb} {effect}.
                                        - {relationship_negative} if the chemical {relationship.negative_verb} {effect}.
                                        3. No headers, explanations, or extra text may be included in the output.
                                        4. Respond only with lines matching the format above—each line must correspond to a single chemical and its relationship.
                                        5. Handle incomplete or unrelated data as follows:
                                        - If only partial data is given (e.g., some chemicals mentioned but not all effects), include only the chemicals with identifiable effects.
                                        - If no relevant data (chemicals or {effect} effects) is provided, output "none".
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

    def find_relationships(self, text: str, chemicals: list[Chemical], effects: list[Effect], relationship_type: RelationshipType) -> list[Relationship]:
        """Find relationships between chemicals and effects.

        Args:
            text (str): The input text.
            chemicals (list[Chemical]): List of chemical entities.
            effects (list[Effect]): List of effect entities.
        """
        relationships = []
        for chemical, effect in product(chemicals, effects):
            if relationship := self._classify_relationship(text, chemical, effect, relationship_type):
                relationships.append(Relationship(relationship_type=relationship_type, chemical=chemical, effect=effect, context=text))
        return relationships
    
    def _classify_relationship(self, text: str, chemical: Chemical, effect: Effect, relationship_type: RelationshipType) -> Relationship | None:
        """Classify the relationship between a chemical and an effect.

        Args:
            text (str): The input text.
            chemical (Chemical): The chemical entity.
            effect (Effect): The effect entity.
        """
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            top_p=self.top_p,
            messages=[
                {
                    "role": self.role,
                    "content": self.relationship_prompt.format(text=text, chemical=chemical.name, effect=effect.name),
                },
            ],
        )
        if response := completion.choices[0].message.content.strip().lower():
            return self._select_relationship_type(response, chemical, effect)
        return None

    def _select_relationship_type(self, response: str, chemical: Chemical, effect: Effect) -> Relationship | None:
        """Select the relationship type based on the response.

        Args:
            response (str): The response from the model indicating the relationship type.
            chemical (Chemical): The chemical entity.
            effect (Effect): The effect entity.
        """
        if response in self.relationship_types:
            relationship_type = self.relationship_types[response]
            if relationship_type is not None:
                return Relationship(relationship=relationship_type, chemical=chemical, effect=effect)
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

    def find_relationships_in_image(self, image_path: str, effects: list[Effect]) -> list[Relationship]:
        """Find relationships between chemicals and effects in an image.

        Args:
            image_path (str): Path to the image.
            effects (list[Effect]): List of effect entities.
        """
        relationships = []
        for effect in effects:
            relationships.extend(self._classify_relationships_in_image(image_path, effect))
        return relationships

    def _classify_relationships_in_image(self, image_path: str, effect: Effect) -> list[Relationship]:
        """Classify relationships between chemicals and an effect in an image.

        Args:
            image_path (str): Path to the image.
            effect (Effect): The effect entity.

        Returns:
            list[Relationship]: List of relationships found in the image.
        """
        base64_image = self._encode_image(image_path)

        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            top_p=self.top_p,
            messages=[
                {
                    "role": self.role,
                    "content": [
                        {"type": "text", "text": self.relationships_image_prompt.format(effect=effect.name)},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                    ],
                },
            ],
        )
        if (content := completion.choices[0].message.content) and (response := content.strip().lower()):
            print(content)
            return self._process_image_response(response, effect)
        return []

    def _encode_image(self, image_path: str) -> str:
        with Path(image_path).open("rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _process_image_response(self, response: str, effect: Effect) -> list[Relationship]:
        relationships = []
        for raw_line in response.splitlines():
            line = raw_line.strip()
            if " : " not in line:
                continue

            chem_name, classification = line.split(" : ", 1)
            chem_name = chem_name.strip().lower()
            classification = classification.strip().lower()

            relationship_type = self.relationship_types.get(classification)
            if relationship_type is None:
                continue

            relationships.append(
                Relationship(relationship=relationship_type, chemical=Chemical(name=chem_name), effect=effect),
            )

        return relationships