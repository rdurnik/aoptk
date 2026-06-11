import os
from pathlib import Path
from Bio import Entrez
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.literature.query import Query

email = os.environ.get("EMAIL") or None
api_key = os.environ.get("NCBI_API_KEY") or None


only_preprint = False
licensing = None
full_text_subset = True

search_term = "hepg2 thioacetamide"

query = Query(
    search_term=search_term,
    full_text_subset=full_text_subset,
    only_preprint=only_preprint,
    licensing=licensing,
)

Entrez.email = email
Entrez.api_key = api_key

ids = EuropePMC(storage="./", figure_storage="./figures", query=query).get_ids()


with Path.open("ids.txt", "w") as f:
    f.writelines(f"{pub_id}{os.linesep}" for pub_id in ids)
