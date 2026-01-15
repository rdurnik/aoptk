from __future__ import annotations
import os
from itertools import product
from dotenv import load_dotenv
from openai import OpenAI
from aoptk.chemical import Chemical
from aoptk.effect import Effect
from aoptk.find_chemical import FindChemical
from aoptk.relationships.find_relationship import FindRelationships
from aoptk.relationships.relationship import Relationship
from aoptk.abbreviations.abbreviation_translator import AbbreviationTranslator


class TextGenerationAPI(FindChemical, FindRelationships, AbbreviationTranslator):
    role: str = "user"
    load_dotenv()
    client: None = None

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

    def find_relationships(self, text: str, chemicals: list[Chemical], effects: list[Effect]) -> list[Relationship]:
        """Find relationships between chemicals and effects."""
        relationships = []
        for chemical, effect in product(chemicals, effects):
            if relationship := self._classify_relationship(text, chemical, effect):
                relationships.append(relationship)
        return relationships

    def _classify_relationship(self, text: str, chemical: Chemical, effect: Effect) -> Relationship | None:
        """Classify the relationship between a chemical and an effect."""
        completion = self.client.chat.completions.create(
            model="gpt-oss-120b",
            messages=[
                {
                    "role": self.role,
                   "content": f"""
                                You are performing a STRICT text-based classification task.

                                Rules:
                                1. Use ONLY the information explicitly stated in the Context.
                                2. Do NOT use biological knowledge, assumptions, or inferred relationships.
                                3. Do NOT assume causal chains or indirect effects.
                                4. Ignore inhibitory relationships completely. 
                                - If the Context says the chemical inhibits or does not inhibit the effect, treat it as if no relationship exists.

                                Effect synonyms:
                                - Treat common synonyms or equivalent terms as the same effect.
                                For example:
                                    - "liver fibrosis" = "hepatic fibrosis"
                                    - "heart attack" = "myocardial infarction"
                                    - "kidney injury" = "renal injury"
                                Always map any synonym in the Context to the target effect before evaluating.

                                Relationship definition:
                                - A relationship exists ONLY IF the Context contains a clear, explicit statement
                                that {chemical} causes or does not cause {effect} (or its synonyms).
                                - Do NOT count statements about inhibition or non-inhibition.

                                Output:
                                - If {chemical} explicitly causes {effect}, return:
                                    - positive
                                - If {chemical} explicitly does not cause {effect}, return:
                                    - negative
                                - In all other cases (including inhibitory statements), return:
                                    - none

                                Do NOT output anything else. No explanations, no extra text.

                                Context:
                                {text}
                                """

                },
            ],
        )
        if answer := completion.choices[0].message.content.strip().lower():
            if answer == "positive":
                return Relationship(relationship="positive", chemical=chemical, effect=effect)
            if answer == "negative":
                return Relationship(relationship="negative", chemical=chemical, effect=effect)
            if answer == "inhibitory":
                return Relationship(relationship="inhibitory", chemical=chemical, effect=effect)
            if answer == "non-inhibitory":
                return Relationship(relationship="non-inhibitory", chemical=chemical, effect=effect)
        return None

    # write some function to get the message - it will be useful for testing purposes

    # def _select_relationship_type(self, top_label: str, classes_verbalized: list[str]) -> str | None:
    #     """Select the relationship type based on the top label."""
    #     if answer == classes_verbalized[0]:
    #         return "positive"
    #     if top_label == classes_verbalized[1]:
    #         return "negative"
    #     return None

    def find_chemical(self, text: str) -> list[Chemical]:
        """Find chemicals in the given text."""
        completion = self.client.chat.completions.create(
            model="gpt-oss-120b",
            messages=[
                {
                    "role": self.role,
                    "content": f"""
                                You are an entity extraction assistant. Your task is to extract chemical entities from the given text.

                                A chemical entity includes:
                                - Full chemical names (e.g., acetaminophen, thioacetamide)
                                - Chemical abbreviations or acronyms (e.g., TAA, APAP, LPS)
                                - Short chemical codes commonly used in scientific writing

                                Instructions:
                                1. Only return chemical names. Do NOT include any extra text, explanations, or punctuation.
                                2. Separate chemical names **exactly** with " ; " (space-semicolon-space). No trailing or leading separators.
                                3. If the text contains no chemicals, return an empty string.

                                Context:
                                {text}
                                """
                },
            ],
        )
        response = completion.choices[0].message.content
        if response is None:
            return []
        return [Chemical(name=chem.strip().lower()) for chem in response.split(" ; ")] if response.strip() else []

    def translate_abbreviation(self, text: str) -> str:
        completion = self.client.chat.completions.create(
            model="gpt-oss-120b",
            messages=[
                {
                    "role": self.role,
                    "content": f"""
                                    You are expanding abbreviations in scientific and biomedical text.

                                    TASK:
                                    Rewrite the input text by replacing abbreviations with their full forms.

                                    SCOPE:
                                    - Expand ONLY:
                                    1) Chemical entities (chemicals, compounds, pollutants)
                                    2) Biological effects or processes (e.g., cell activation, toxicity, fibrosis-related events)
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

                                    OUTPUT:
                                    - Return ONLY the rewritten text.
                                    - Do NOT add explanations, comments, or formatting.

                                    INPUT TEXT:
                                    {text}
                                    """,
                },
            ],
        )
        response = completion.choices[0].message.content
        return response if response is not None else text