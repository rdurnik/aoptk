from dataclasses import dataclass


@dataclass
class Effect:
    """Data structure representing a biological effect (adverse outcome / key event)."""

    effect: str

    def __str__(self) -> str:
        return self.effect
