from __future__ import annotations
from datetime import datetime
import click
import pandas as pd
from Bio import Entrez
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.literature.databases.pubmed import PubMed
from aoptk.spacy_processor import Spacy


def generate_list_of_relevant_chemicals(use_tg_gates: str, use_tox21: str, user_defined_database: str) -> list[str]:
    """Generate a list of relevant chemicals from Excel file."""
    list_of_relevant_chemicals = []
    if use_tg_gates:
        relevant_chemicals_database = pd.read_excel(use_tg_gates)
        list_of_relevant_chemicals.extend(
            relevant_chemicals_database["chemical_name"].astype(str).str.lower().unique().tolist(),
        )
    if use_tox21:
        relevant_chemicals_database = pd.read_excel(use_tox21)
        list_of_relevant_chemicals.extend(
            relevant_chemicals_database["chemical_name"].astype(str).str.lower().unique().tolist(),
        )
    if user_defined_database:
        relevant_chemicals_database = pd.read_excel(user_defined_database)
        list_of_relevant_chemicals.extend(
            relevant_chemicals_database["chemical_name"].astype(str).str.lower().unique().tolist(),
        )
    return list_of_relevant_chemicals


def find_relevant_chemicals(
    use_mesh_terms: str,
    list_of_relevant_chemicals: list[str],
    chemicals: list[str],
) -> list[str]:
    """Find chemical names that are in the list of relevant chemicals."""
    relevant_chemicals = []
    for chemical in chemicals:
        if chemical.name.lower() in list_of_relevant_chemicals:
            relevant_chemicals.append(chemical.name)
        elif use_mesh_terms == "yes":
            try_to_match_mesh_term_to_relevant_chemical(list_of_relevant_chemicals, relevant_chemicals, chemical)
    return relevant_chemicals


def try_to_match_mesh_term_to_relevant_chemical(
    list_of_relevant_chemicals: list[str],
    relevant_chemicals: list[str],
    chemical: str,
) -> None:
    """Try to match MeSH terms generated from chemical name to relevant chemicals."""
    if mesh_terms := Spacy().generate_mesh_terms(chemical.name):
        for term in mesh_terms:
            if term in list_of_relevant_chemicals:
                relevant_chemicals.append(term)
                break


@click.command()
@click.option("--use_tg_gates", type=str, required=False, help="Use TG-GATES chemical database (yes/no)")
@click.option("--use_tox21", type=str, required=False, help="Use Tox21 chemical database (yes/no)")
@click.option(
    "--user_defined_database",
    type=str,
    default=None,
    required=False,
    help="Path to the user-defined chemical database in Excel (optional)",
)
@click.option("--email", type=str, required=True, help="Email address to follow PubMed - NCBI guidelines")
@click.option(
    "--query",
    type=str,
    required=True,
    default='("liver") AND ("fibrotic" OR "fibrosis") AND ("spheroid*" OR "organoid*" OR "multicellular" OR "coculture*" OR "in vitro model") AND ("1900/01/01"[PDAT] : "2025/07/25"[PDAT])',
    help="Search term for PubMed or Europe PMC",
)
@click.option(
    "--literature_database",
    type=click.Choice(["pubmed", "europepmc"]),
    required=True,
    help="Database to search: PubMed or Europe PMC",
)
@click.option(
    "--use_mesh_terms",
    type=click.Choice(["yes", "no"]),
    required=True,
    help="Use MeSH terms to normalize chemical names (yes/no)",
)
def cli(
    email: str,
    use_tg_gates: str,
    use_tox21: str,
    user_defined_database: str,
    query: str,
    literature_database: str,
    use_mesh_terms: str,
) -> None:
    """Identify relevant chemicals in abstracts from literature databases."""
    Entrez.email = email
    list_of_relevant_chemicals = generate_list_of_relevant_chemicals(use_tg_gates, use_tox21, user_defined_database)
    if literature_database == "pubmed":
        abstracts = PubMed(query).get_abstracts()
    elif literature_database == "europepmc":
        abstracts = EuropePMC(query).get_abstracts()
    result_df = pd.DataFrame(columns=["publication_id", "chemicals", "relevant_chemicals"])
    for abstract in abstracts:
        publication_id = abstract.publication_id
        chemicals = Spacy().find_chemical(abstract.text)
        chemicals = [chem.trimmed_name for chem in chemicals if chem.name]
        relevant_chemicals = find_relevant_chemicals(use_mesh_terms, list_of_relevant_chemicals, chemicals)
        result_df.loc[len(result_df)] = [
            publication_id,
            {chemical.name for chemical in chemicals},
            set(relevant_chemicals),
        ]
    result_df.to_excel(
        f"src/aoptk/application/{literature_database}_testing_purposes_use_mesh_terms_{use_mesh_terms}_{datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}.xlsx",
        index=False,
    )

    output_df = result_df[result_df["relevant_chemicals"].apply(len) > 0]
    output_df.to_excel(
        f"src/aoptk/application/{literature_database}_identified_chemicals_use_mesh_terms_{use_mesh_terms}_{datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}.xlsx",
        index=False,
    )

    exploded_df = output_df.explode("relevant_chemicals")
    grouped_df = (
        exploded_df.groupby("relevant_chemicals")
        .agg(
            publication_count=("publication_id", "count"),
            publication_id=("publication_id", list),
        )
        .reset_index()
        .sort_values("publication_count", ascending=False)
    )

    grouped_df.to_excel(
        f"src/aoptk/application/{literature_database}_grouped_chemicals_use_mesh_terms_{use_mesh_terms}_{datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}.xlsx",
        index=False,
    )
