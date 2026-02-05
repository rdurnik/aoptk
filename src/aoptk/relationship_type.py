
class RelationshipType:
    """Data structure representing a relationship between a chemical and an effect."""

    def __init__(self, positive: str, positive_verb: str, negative: str, negative_verb: str, definition: str):
        self.positive = positive
        self.positive_verb = positive_verb
        self.negative = negative
        self.negative_verb = negative_verb
        self.definition = definition


class Inhibitive(RelationshipType):
    """Data structure representing an inhibition relationship between a chemical and an effect."""

    def __init__(self):
        super().__init__(
            positive="Inhibition",
            positive_verb="inhibits",
            negative="No inhibition",
            negative_verb="does not inhibit",
            definition="Inhibit means the chemical suppresses, reduces, blocks, or prevents the biological effect. Treat clear synonyms of the effect as equivalent.",
        )

class Causative(RelationshipType):
    """Data structure representing a causative relationship between a chemical and an effect."""

    def __init__(self):
        super().__init__(
            positive="Causation",
            positive_verb="causes",
            negative="No causation",
            negative_verb="does not cause",
            definition="Cause means the chemical brings about, induces, or is responsible for the biological effect. Treat clear synonyms of the effect as equivalent. Do NOT count statements about inhibition or non-inhibition.",
        )