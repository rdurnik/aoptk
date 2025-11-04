from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class Publication:
    id: str # In the final output, user will need a list of IDs based on which the result was concluded (e.g., liver fibrosis is caused by thioacetamide based on publications 1, 2, 3...)
    abstract: str
    non_abstract_text: str
    abbreviations: Optional[Dict[str, str]] = field(default_factory=dict)
    tables: Optional[str] = None
    figures: Optional[str] = None

    def __str__(self) -> str:
        pass # ?