import os
from pathlib import Path
from Bio import Entrez
from aoptk.literature.databases.pubmed import PubMed
from aoptk.literature.id import ID

with Path.open("ids.txt") as f:
    raw_ids = [line.strip() for line in f]
    ids = [ID(pub_id) for pub_id in raw_ids]

Entrez.email = os.environ.get("EMAIL") or None
Entrez.api_key = os.environ.get("NCBI_API_KEY") or None


# if $literature.database == "pmc":
database = PubMed(storage="./abstracts")

Path.mkdir("./abstracts", parents=True)

abstracts = database.get_abstracts(ids=ids)
