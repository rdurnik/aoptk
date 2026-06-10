import os
from Bio import Entrez
from aoptk.literature.databases.pmc import PMC
from aoptk.literature.id import ID

with open("ids.txt") as f:
    ids = [ID(line.strip()) for line in f]

Entrez.email = os.environ.get("EMAIL") or None
Entrez.api_key = os.environ.get("NCBI_API_KEY") or None


database = PMC(storage="./pdfs", figure_storage="./figures")
# database.update_retry_strategy(Retry(total=2))

pdfs = database.get_pdfs(ids=ids)
