import os
from Bio import Entrez
from aoptk.literature.databases.pmc import PMC
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.literature.databases.pubmed import PubMed
from aoptk.literature.id import ID

with open("ids.txt", "r") as f:
    raw_ids = [line.strip() for line in f.readlines()]
    ids = [ID(id) for id in raw_ids]

Entrez.email = os.environ.get("EMAIL") or None
Entrez.api_key = os.environ.get("NCBI_API_KEY") or None


#if $literature.database == "pmc":
database = PubMed()

os.makedirs("./abstracts")

abstracts = database.get_abstracts(ids=ids)
for abstract in abstracts:
    with open(f"./abstracts/{abstract.id}.txt", "w") as f:
        f.write(abstract.text)