import click
import pandas as pd
from Bio import Entrez
from aoptk.literature.databases.pubmed import PubMed
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.spacy import Spacy
from aoptk.normalization.mesh_terms import MeshTerms
from aoptk.normalization.provide_mesh_term_dataframe_from_xml import ProvideMeshTermDataframeFromXML

def generate_list_of_relevant_chemicals(use_tg_gates, use_tox21, user_defined_database):
    list_of_relevant_chemicals = []
    if use_tg_gates:
        process_database(use_tg_gates, list_of_relevant_chemicals)
    if use_tox21:
        process_database(use_tox21, list_of_relevant_chemicals)
    if user_defined_database:
        process_database(user_defined_database, list_of_relevant_chemicals)
    return list_of_relevant_chemicals


def process_database(path_to_relevant_chemicals_database, list_of_relevant_chemicals):
    relevant_chemicals_database = pd.read_excel(path_to_relevant_chemicals_database)
    list_of_relevant_chemicals.extend(relevant_chemicals_database['chemical_name'].astype(str).str.lower().unique().tolist())
    list_of_relevant_chemicals.append(path_to_relevant_chemicals_database)


def normalize_chemical(chemicals, mesh_normalization_dataframe):
    normalized_chemicals = []
    for chemical in chemicals:
        normalized_chemical = MeshTerms(mesh_normalization_dataframe).normalize_chemical(chemical)
        normalized_chemicals.append(normalized_chemical)
    return normalized_chemicals


@click.command()
@click.option('--use_tg_gates', 
              type=str, 
              required=False, 
              help='Use TG-GATES chemical database (yes/no)')
@click.option('--use_tox21', 
              type=str, 
              required=False, 
              help='Use Tox21 chemical database (yes/no)')
@click.option('--user_defined_database', 
              type=str, 
              default=None, 
              required=False, 
              help='Path to the user-defined chemical database in Excel (optional)')
# @click.option('--email', 
#               type=str, 
#               required=True, 
#               help='Email address to follow PubMed - NCBI guidelines')
@click.option('--query', 
              type=str, 
              required=True, 
              help='Search term for PubMed or Europe PMC')
@click.option('--literature_database', 
              type=click.Choice(['pubmed', 'europepmc']), 
              required=True, 
              help='Database to search: PubMed or Europe PMC')
@click.option('--use_mesh_terms', 
              type=click.Choice(['yes', 'no']), 
              required=True, 
              help='Use MeSH terms to normalize chemical names (yes/no)')
def main(use_tg_gates, use_tox21, user_defined_database, query, literature_database, use_mesh_terms):
    list_of_relevant_chemicals = generate_list_of_relevant_chemicals(use_tg_gates, use_tox21, user_defined_database)
    if literature_database == 'pubmed':
        abstracts = PubMed(query).get_abstracts()
    elif literature_database == 'europepmc':
        abstracts = EuropePMC(query).get_abstracts()
    mesh_normalization_dataframe = ProvideMeshTermDataframeFromXML('src/aoptk/application/full_mesh_term_database.xml').provide_normalization_dataframe()
    result_df = pd.DataFrame(columns=['publication_id', 'chemicals', 'relevant_chemicals'])
    for abstract in abstracts[0:5]:
        id = abstract.publication_id
        chemicals = Spacy().find_chemical(abstract.text)
        if use_mesh_terms == 'yes':
            chemicals = normalize_chemical(chemicals, mesh_normalization_dataframe)
        relevant_chemicals = []
        for chemical in chemicals:
            if chemical.name in list_of_relevant_chemicals:
                relevant_chemicals.append(chemical.name)

        result_df.loc[len(result_df)] = [id, set([chemical.name for chemical in chemicals]), set(relevant_chemicals)]
    result_df.to_csv('src/aoptk/application/identified_chemicals.csv', index=False)


if __name__ == "__main__":
    main()