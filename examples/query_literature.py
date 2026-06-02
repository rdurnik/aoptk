import asyncio
from Bio import Entrez
import os
from aoptk.literature.databases.pubmed import PubMed
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.literature.databases.pmc import PMC
from aoptk.literature.query import Query 

email = os.environ.get("EMAIL") or None
api_key = os.environ.get("NCBI_API_KEY") or None


only_preprint = False
licensing = None
full_text_subset = True

search_term = "hepg2 thioacetamide"

query = Query(search_term=search_term, full_text_subset=full_text_subset, only_preprint=only_preprint, licensing=licensing)

Entrez.email = email
Entrez.api_key = api_key

ids = EuropePMC(storage = "./", figure_storage="./figures", query=query).get_ids()


with open(f"ids.txt", "w") as f:
    for id in ids:
        f.write(f"{id}{os.linesep}")