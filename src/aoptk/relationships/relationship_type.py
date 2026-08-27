class RelationshipType:
    """Data structure representing a relationship between a chemical and an effect."""

    def __init__(self, positive: str, positive_verb: str, negative: str, negative_verb: str, definition: str):
        self.positive = positive
        self.positive_verb = positive_verb
        self.negative = negative
        self.negative_verb = negative_verb
        self.definition = definition

    def __eq__(self, other: object) -> bool:
        """Compare two relationship types by their positive label."""
        return isinstance(other, RelationshipType) and self.positive == other.positive

    def __hash__(self) -> int:
        """Hash a relationship type by its positive label."""
        return hash(self.positive)

    def __repr__(self) -> str:
        """Human-readable representation of a relationship type."""
        return f"{self.__class__.__name__}(positive={self.positive!r})"


class Inhibition(RelationshipType):
    """Data structure representing an inhibition relationship between a chemical and an effect.

    Inhibition covers the chemical blocking, suppressing, or reducing an existing or
    ongoing process (e.g. an enzyme or pathway). Unlike Prevention, it does not require
    the effect to be averted before it starts, and unlike Alleviation, it does not imply
    a therapeutic benefit to the organism.
    """

    def __init__(self):
        super().__init__(
            positive="inhibition",
            positive_verb="inhibits",
            negative="no inhibition",
            negative_verb="does not inhibit",
            definition=(
                "Inhibit means the chemical blocks, suppresses, or reduces the activity of the biological effect, "
                "for example by blocking an enzyme or pathway. The effect is a biological process or activity; "
                "the chemical reduces its level or rate. Do not classify as inhibition if the effect is averted "
                "before it occurs (prevention), if the statement describes a therapeutic benefit to the organism "
                "(alleviation or mitigation), or if the chemical starts or switches the effect on (activation or "
                "stimulation)."
            ),
        )


class Causation(RelationshipType):
    """Data structure representing a causation relationship between a chemical and an effect.

    Causation covers the chemical bringing about, inducing, or being responsible for the
    effect. Unlike Promotion, causation states the chemical directly brings the effect
    about; unlike Induction, it does not specifically refer to triggering a response or
    expression.
    """

    def __init__(self):
        super().__init__(
            positive="causation",
            positive_verb="causes",
            negative="no causation",
            negative_verb="does not cause",
            definition=(
                "Cause means the chemical brings about, induces, or is responsible for the biological effect. "
                "The chemical is the direct source or trigger of the effect. Do not classify as causation if the "
                "chemical only favors, encourages, or increases the likelihood of the effect over time (promotion), "
                "if the statement specifically describes triggered expression, differentiation, or a physiological "
                "response (induction), or if the chemical reduces, blocks, or averts the effect (inhibition, "
                "prevention, alleviation, mitigation, or regulation)."
            ),
        )


class Activation(RelationshipType):
    """Data structure representing an activation relationship between a chemical and an effect.

    Activation covers the chemical switching on, stimulating, or turning on a biological
    process (e.g. a receptor, channel, or pathway). Unlike Causation, the focus is on the
    process moving from an inactive to an active state; unlike Promotion, it is an on/off
    mechanism rather than a gradual increase over time.
    """

    def __init__(self):
        super().__init__(
            positive="activation",
            positive_verb="activates",
            negative="no activation",
            negative_verb="does not activate",
            definition=(
                "Activate means the chemical switches on, stimulates, or turns on the biological effect, for "
                "example a receptor, ion channel, or signaling pathway. The effect moves from an inactive to an "
                "active state. Do not classify as activation if the chemical only increases the rate or likelihood "
                "of the effect over time (promotion), if it broadly brings the effect about (causation), or if it "
                "reduces or blocks the effect (inhibition or regulation)."
            ),
        )


class Promotion(RelationshipType):
    """Data structure representing a promotion relationship between a chemical and an effect.

    Promotion covers the chemical favoring, encouraging, increasing, or facilitating the
    effect (e.g. promoting proliferation). Unlike Causation, promotion does not require
    the chemical to be the direct source of the effect; unlike Activation, it describes a
    gradual increase or facilitation rather than switching the effect on.
    """

    def __init__(self):
        super().__init__(
            positive="promotion",
            positive_verb="promotes",
            negative="no promotion",
            negative_verb="does not promote",
            definition=(
                "Promote means the chemical favors, encourages, increases, or facilitates the biological effect, "
                "for example by promoting cell proliferation or disease progression. The effect is a process the "
                "chemical makes more likely, more frequent, or more extensive. Do not classify as promotion if the "
                "chemical directly brings the effect about (causation), if the statement is about switching a "
                "mechanism on (activation), or if the chemical reduces or averts the effect (inhibition, "
                "prevention, alleviation, mitigation, or regulation)."
            ),
        )


class Prevention(RelationshipType):
    """Data structure representing a prevention relationship between a chemical and an effect.

    Prevention covers the chemical averting, protecting against, or preventing the effect
    from occurring. Unlike Inhibition, the effect never starts or is stopped before onset;
    unlike Alleviation, the effect is averted before it becomes present.
    """

    def __init__(self):
        super().__init__(
            positive="prevention",
            positive_verb="prevents",
            negative="no prevention",
            negative_verb="does not prevent",
            definition=(
                "Prevent means the chemical averts, protects against, or stops the biological effect from "
                "occurring. The effect does not develop because the chemical was present. Do not classify as "
                "prevention if the effect is already underway and the chemical reduces it (inhibition), if the "
                "effect is already present and the chemical eases it (alleviation or mitigation), or if the "
                "chemical brings the effect about (causation, promotion, activation, or regulation)."
            ),
        )


class Induction(RelationshipType):
    """Data structure representing an induction relationship between a chemical and an effect.

    Induction covers the chemical triggering, eliciting, or turning on a response,
    expression, or physiological state (e.g. inducing gene expression or apoptosis).
    Like Causation it is a positive, initiating direction, but it is specific to triggered
    responses rather than to bringing an effect about in general.
    """

    def __init__(self):
        super().__init__(
            positive="induction",
            positive_verb="induces",
            negative="no induction",
            negative_verb="does not induce",
            definition=(
                "Induce means the chemical triggers, elicits, or turns on the biological effect, for example "
                "gene expression, apoptosis, or a physiological response. The effect is a response or state that "
                "the chemical starts. Use induction when the statement specifically describes triggering an "
                "expression, differentiation, or response; for general statements that the chemical brings the "
                "effect about, use causation instead. Do not classify as induction if the chemical reduces, "
                "blocks, or averts the effect (inhibition, prevention, alleviation, mitigation, or "
                "regulation)."
            ),
        )


class Alleviation(RelationshipType):
    """Data structure representing an alleviation relationship between a chemical and an effect.

    Alleviation covers the chemical relieving, easing, or reducing the severity of an
    effect already experienced (e.g. alleviating inflammation). Unlike Prevention, the
    effect is already present; unlike Mitigation, alleviation emphasizes symptomatic
    relief.
    """

    def __init__(self):
        super().__init__(
            positive="alleviation",
            positive_verb="alleviates",
            negative="no alleviation",
            negative_verb="does not alleviate",
            definition=(
                "Alleviate means the chemical relieves, eases, or reduces the severity of the biological effect, "
                "for example alleviating pain or inflammation. The effect is already present and the chemical "
                "makes it less severe. Do not classify as alleviation if the effect is averted before it occurs "
                "(prevention), if the chemical blocks the underlying process (inhibition), or if the chemical "
                "reduces the overall risk or harm (mitigation)."
            ),
        )


class Mitigation(RelationshipType):
    """Data structure representing a mitigation relationship between a chemical and an effect.

    Mitigation covers the chemical lessening, moderating, or reducing the severity or
    impact of the effect. It is the protective, harm-reducing counterpart to Promotion;
    unlike Alleviation, it emphasizes reducing risk or harm rather than easing symptoms.
    """

    def __init__(self):
        super().__init__(
            positive="mitigation",
            positive_verb="mitigates",
            negative="no mitigation",
            negative_verb="does not mitigate",
            definition=(
                "Mitigate means the chemical lessens, moderates, or reduces the severity, impact, or risk of the "
                "biological effect. The chemical reduces the harm the effect causes. Do not classify as "
                "mitigation if the effect is averted entirely before onset (prevention), if the chemical blocks "
                "the underlying process (inhibition), or if it eases an existing symptom (alleviation)."
            ),
        )


class Regulation(RelationshipType):
    """Data structure representing a regulation relationship between a chemical and an effect.

    Regulation covers the chemical modulating the level or expression of the effect
    (e.g. gene or protein expression). It is directional: a level increase is reported
    as upregulation (positive), a level decrease as downregulation (negative). Unlike
    Inhibition, it is specific to the expression or abundance level of a molecular
    target; unlike Causation and Promotion, it states how the level changes, not that
    the chemical brings the effect about.
    """

    def __init__(self):
        super().__init__(
            positive="upregulation",
            positive_verb="upregulates",
            negative="downregulation",
            negative_verb="downregulates",
            definition=(
                "Regulate means the chemical modulates the level or expression of the biological effect, for "
                "example the expression or abundance of a gene or protein. The effect is a molecular target whose "
                "level changes. Return upregulation if the chemical increases the level and downregulation if it "
                "decreases the level. Do not classify as regulation if the statement is about triggering a "
                "response or expression without specifying an increase or decrease in level (induction), or about "
                "blocking an existing process rather than changing an expression level (inhibition)."
            ),
        )
