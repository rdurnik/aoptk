import click
import pandas as pd
from Bio import Entrez
from aoptk.literature.databases.pubmed import PubMed
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.spacy_processor import Spacy
from datetime import datetime
import spacy
from scispacy.linking import EntityLinker  

def generate_list_of_relevant_chemicals(use_tg_gates, use_tox21, user_defined_database):
    list_of_relevant_chemicals = []
    if use_tg_gates:
        relevant_chemicals_database = pd.read_excel(use_tg_gates)
        list_of_relevant_chemicals.extend(relevant_chemicals_database['chemical_name'].astype(str).str.lower().unique().tolist())
    if use_tox21:
        relevant_chemicals_database = pd.read_excel(use_tox21)
        list_of_relevant_chemicals.extend(relevant_chemicals_database['chemical_name'].astype(str).str.lower().unique().tolist())
    if user_defined_database:
        relevant_chemicals_database = pd.read_excel(user_defined_database)
        list_of_relevant_chemicals.extend(relevant_chemicals_database['chemical_name'].astype(str).str.lower().unique().tolist())
    return list_of_relevant_chemicals

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
@click.option('--email', 
              type=str, 
              required=True, 
              help='Email address to follow PubMed - NCBI guidelines')
@click.option('--query', 
              type=str, 
              required=True,
              default='(("liver") AND ("fibrotic" OR "fibrosis") AND ("spheroid*" OR "organoid*" OR "multicellular" OR "coculture*" OR "in vitro model")) AND (("1983"[Date - Entry] : "2025/07/25"[Date - Entry]))',
              help='Search term for PubMed or Europe PMC')
@click.option('--literature_database', 
              type=click.Choice(['pubmed', 'europepmc']), 
              required=True, 
              help='Database to search: PubMed or Europe PMC')
@click.option('--use_mesh_terms', 
              type=click.Choice(['yes', 'no']), 
              required=True, 
              help='Use MeSH terms to normalize chemical names (yes/no)')
def main(email, use_tg_gates, use_tox21, user_defined_database, query, literature_database, use_mesh_terms):
    Entrez.email = email
    list_of_relevant_chemicals = generate_list_of_relevant_chemicals(use_tg_gates, use_tox21, user_defined_database)
    if literature_database == 'pubmed':
        abstracts = PubMed(query).get_abstracts()
    elif literature_database == 'europepmc':
        abstracts = EuropePMC(query).get_abstracts()
    print(abstracts)
    result_df = pd.DataFrame(columns=['publication_id', 'chemicals', 'relevant_chemicals'])
    for abstract in abstracts:
        id = abstract.publication_id
        print(abstract)
        chemicals = Spacy().find_chemical(abstract.text)
        chemicals = [chem for chem in chemicals if chem.name]
        cleaned_chemicals = []
        for chem in chemicals:
            if '-treated' in chem.name.lower() or '-induced' in chem.name.lower():
                cleaned_name = chem.name.rsplit('-', 1)[0].strip()
                chem = type(chem)(cleaned_name)
            cleaned_chemicals.append(chem)
        chemicals = cleaned_chemicals
        print([chem.name for chem in chemicals])
        relevant_chemicals = []
        for chemical in chemicals:
            if chemical.name.lower() in list_of_relevant_chemicals:
                relevant_chemicals.append(chemical.name)
            elif use_mesh_terms == 'yes':
                if mesh_terms := Spacy().generate_mesh_terms(chemical.name):
                    for term in mesh_terms:
                        if term in list_of_relevant_chemicals:
                            relevant_chemicals.append(term)
                            break
        result_df.loc[len(result_df)] = [id, set([chemical.name for chemical in chemicals]), set(relevant_chemicals)]
    
    result_df = result_df[result_df['relevant_chemicals'].apply(len) > 0]
    result_df.to_csv(f'src/aoptk/application/{literature_database}_identified_chemicals_use_mesh_terms_{use_mesh_terms}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv', index=False)


    result_df = result_df.explode('relevant_chemicals')
    grouped_df = result_df.groupby('relevant_chemicals').agg(
        publication_count=('publication_id', 'count'),
        publication_id=('publication_id', list)
    ).reset_index().sort_values('publication_count', ascending=False)

    grouped_df.to_csv(f'src/aoptk/application/{literature_database}_grouped_chemicals_use_mesh_terms_{use_mesh_terms}{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv', index=False)


if __name__ == "__main__":
    main()