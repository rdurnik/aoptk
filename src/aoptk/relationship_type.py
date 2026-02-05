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
            positive="inhibition",
            positive_verb="inhibits",
            negative="no inhibition",
            negative_verb="does not inhibit",
            definition="Inhibit means the chemical suppresses, reduces, blocks, or prevents the biological effect. "
        )


class Causative(RelationshipType):
    """Data structure representing a causative relationship between a chemical and an effect."""

    def __init__(self):
        super().__init__(
            positive="causation",
            positive_verb="causes",
            negative="no causation",
            negative_verb="does not cause",
            definition="Cause means the chemical brings about, induces, or is responsible for the biological effect."
        )
