import os
from pathlib import Path
from Bio import Entrez
from aoptk.literature.databases.pmc import PMC
from aoptk.literature.id import ID

with Path("ids.txt").open("r") as f:
    ids = [ID(line.strip()) for line in f]

Entrez.email = os.environ.get("EMAIL") or None
Entrez.api_key = os.environ.get("NCBI_API_KEY") or None


database = PMC(storage="./pdfs", figure_storage="./figures")

pdfs = database.get_pdfs(ids=ids)
