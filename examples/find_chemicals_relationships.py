import os
from pathlib import Path
import pandas as pd
from aoptk.chemical import Chemical
from aoptk.effect import Effect
from aoptk.relationships.relationship import Relationship
from aoptk.relationships.relationship_type import Causative
from aoptk.relationships.relationship_type import Inhibitive
from aoptk.text_generation_api import LLMFailureError
from aoptk.text_generation_api import TextGenerationAPI

litellm_api_key = os.getenv("LITELLM_API_KEY")


def write_relationships(publication_id: str, relationships: list[Relationship]) -> None:
    """Writes the relationships to a TSV file."""
    Path("relationships").mkdir(exist_ok=True)
    with Path.open(f"relationships/{publication_id}.tsv", "w") as f_out:
        f_out.write("id\tchemical\teffect\trelationship\n")
        f_out.writelines(
            f"{publication_id}\t{relationship.chemical}\t{relationship.effect}\t{relationship.relationship_type}\n"
            for relationship in relationships
        )


def write_chemicals(publication_id: str, chemicals: list[Chemical]) -> None:
    """Writes the chemicals to a TSV file."""
    Path("chemicals").mkdir(exist_ok=True)
    df = pd.DataFrame([chem.to_dict() for chem in chemicals])
    df.to_csv(f"chemicals/{publication_id}.tsv", sep="\t", index=False)


publications = list(Path("publications").iterdir())[:3]
effects = [Effect("liver fibrosis"), Effect("liver cell death")]
relationship_types = [Causative(), Inhibitive()]

completed = []
retry = []
failed = []
is_retry = False

while publications or retry:
    if publications:
        publication = publications.pop()
        is_retry = False
    elif retry:
        publication = retry.pop()
        is_retry = True

    with Path.open(publication) as f_in:
        text = f_in.read()

    publication_id = Path(publication).stem

    if not Path(f"chemicals/{publication_id}.tsv").exists():
        try:
            chemicals = TextGenerationAPI(model="gpt-oss-120b", api_key=litellm_api_key).find_chemicals(text)
            write_chemicals(publication_id, chemicals)
        except LLMFailureError:
            if is_retry:
                failed.append(publication)
            else:
                retry.append(publication)
            continue

    try:
        chemicals = pd.read_csv(f"chemicals/{publication_id}.tsv", sep="\t")["name"].tolist()
        relationships = TextGenerationAPI(model="gpt-oss-120b", api_key=litellm_api_key).find_relationships_in_text(
            text=text,
            chemicals=[Chemical(name=name) for name in chemicals],
            effects=effects,
            relationship_types=relationship_types,
        )
        write_relationships(publication_id, relationships)
    except LLMFailureError:
        if is_retry:
            failed.append(publication)
        else:
            retry.append(publication)
        continue
