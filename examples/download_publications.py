import os
from pathlib import Path
from Bio import Entrez
from aoptk.literature.databases.pmc import PMC
from aoptk.literature.id import ID

with Path.open("ids.txt") as f:
    raw_ids = [line.strip() for line in f]
    ids = [ID(publication_id) for publication_id in raw_ids]

Entrez.email = os.environ.get("EMAIL") or None
Entrez.api_key = os.environ.get("NCBI_API_KEY") or None


# if $literature.database == "pmc":
database = PMC(storage="./publications", figure_storage="./figures")


publications = database.get_publications(ids=ids, download_figures_enabled=False)
