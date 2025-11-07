from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class Publication:
    id: str # In the final output, user will need a list of IDs based on which the result was concluded (e.g., liver fibrosis is caused by thioacetamide based on publications 1, 2, 3...).
    # If user provides their own PDFs, the ID could simply be the filename.
    abstract: str
    full_text: str
    abbreviations: Optional[Dict[str, str]] = field(default_factory=dict)
    tables: Optional[str] = None
    figures: Optional[str] = None
    figure_description: Optional[str] = None

    def __str__(self) -> str:
        pass # ?