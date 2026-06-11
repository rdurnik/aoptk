import os
from pathlib import Path
from Bio import Entrez
from aoptk.literature.databases.pmc import PMC
from aoptk.literature.id import ID

with Path("ids.txt").open("r") as f:
    raw_ids = [line.strip() for line in f]
    ids = [ID(pub_id) for pub_id in raw_ids]

Entrez.email = os.environ.get("EMAIL") or None
Entrez.api_key = os.environ.get("NCBI_API_KEY") or None


# if $literature.database == "pmc":
database = PMC(storage="./abstracts", figure_storage="./figures")

abstracts = database.get_abstracts(ids=ids)
