from __future__ import annotations
from pathlib import Path
import click
import pandas as pd
from Bio import Entrez
from aoptk.chemical import Chemical
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.literature.databases.pubmed import PubMed
from aoptk.spacy_processor import Spacy


@click.command()
@click.option(
    "--query",
    type=str,
    required=True,
    help="Search term for PubMed or Europe PMC",
)
@click.option(
    "--literature_database",
    type=click.Choice(["pubmed", "europepmc"]),
    required=True,
    help="Database to search: PubMed or Europe PMC",
)
@click.option(
    "--chemical_database",
    type=str,
    required=True,
    help="Path to the user-defined chemical database in Excel (optional)",
)
@click.option(
    "--email",
    type=str,
    required=False,
    default=None,
    help="Email address to follow PubMed - NCBI guidelines",
)
@click.option("--outdir", "-o", type=str, required=True, help="Output directory.")
def cli(query: str, literature_database: str, chemical_database: str, email: str, outdir: str) -> None:
    """Identify relevant chemicals in abstracts from literature databases.

    Args:
        query (str): Search term for PubMed or Europe PMC.
        literature_database (str): Database to search: PubMed or Europe PMC.
        chemical_database (str): Path to the user-defined chemical database in Excel.
        email (str): Email address to follow PubMed - NCBI guidelines.
        outdir (str): Output directory.
    """
    database_with_ids = generate_database_with_ids(query, literature_database, email)

    abstracts = database_with_ids.get_abstracts()

    list_of_relevant_chemicals = generate_relevant_chemicals(chemical_database)
    result_df = pd.DataFrame(columns=["publication_id", "chemicals"])
    for abstract in abstracts:
        chemicals = Spacy().find_chemical(abstract.text)
        normalized_chemicals = [Spacy().normalize_chemical(chem) for chem in chemicals]
        relevant_chemicals = match_chemicals_with_loose_equality(list_of_relevant_chemicals, normalized_chemicals)

        result_df.loc[len(result_df)] = [
            abstract.publication_id.id_str,
            set(relevant_chemicals),
        ]

    export_results_as_xlsx(result_df, outdir)


def generate_database_with_ids(query: str, literature_database: str, email: str) -> EuropePMC | PubMed | None:
    """Generate an object with IDs from the specified literature database.

    Args:
        query (str): Search term for PubMed or Europe PMC.
        literature_database (str): Database to search: PubMed or Europe PMC.
        email (str): Email address to follow PubMed - NCBI guidelines.
    """
    if literature_database == "pubmed":
        Entrez.email = email
        pubmed = PubMed(query)
        ids = pubmed.get_id()
        pubmed.id_list = ids
        return pubmed
    if literature_database == "europepmc":
        europepmc = EuropePMC(query)
        ids = europepmc.get_id()
        europepmc.id_list = ids
        return europepmc
    return None


def generate_relevant_chemicals(chemical_database: str) -> list[Chemical]:
    """Generate a list of relevant chemicals from Excel file.

    Args:
        chemical_database (str): Path to the user-defined chemical database in Excel.
    """
    relevant_chemicals_database = pd.read_excel(chemical_database)
    return [Chemical(name) for name in relevant_chemicals_database["chemical_name"].astype(str).str.lower().unique()]


def match_chemicals_with_loose_equality(
    list_of_relevant_chemicals: list[Chemical],
    normalized_chemicals: list[Chemical],
) -> list[str]:
    """Match normalized chemicals with relevant chemicals using loose equality.

    Args:
        list_of_relevant_chemicals (list[Chemical]): List of relevant chemicals.
        normalized_chemicals (list[Chemical]): List of normalized chemicals from abstracts.
    """
    relevant_chemicals = []
    for chemical in normalized_chemicals:
        for relevant_chemical in list_of_relevant_chemicals:
            if chemical.similar(relevant_chemical):
                relevant_chemicals.append(chemical.name)
                break
    return relevant_chemicals


def export_results_as_xlsx(result_df: pd.DataFrame, outdir: str) -> None:
    """Export results as Excel files.

    Args:
        result_df (pd.DataFrame): DataFrame containing publication IDs and chemicals.
        outdir (str): Output directory.

    """
    chemicals_per_publication_df = result_df[result_df["chemicals"].apply(len) > 0]
    chemicals_per_publication_df.to_excel(
        Path(outdir) / "chemicals_per_publication.xlsx",
        index=False,
    )

    exploded_chemicals_per_publication_df = chemicals_per_publication_df.explode("chemicals")
    publications_per_chemical = (
        exploded_chemicals_per_publication_df.groupby("chemicals")
        .agg(
            publication_count=("publication_id", "count"),
            publication_id=("publication_id", list),
        )
        .reset_index()
        .sort_values("publication_count", ascending=False)
    )
    publications_per_chemical.to_excel(
        Path(outdir) / "publications_per_chemical.xlsx",
        index=False,
    )
