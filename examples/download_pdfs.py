import os
from Bio import Entrez
from aoptk.literature.databases.pmc import PMC
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.literature.databases.pubmed import PubMed
from aoptk.literature.id import ID
from urllib3.util.retry import Retry

with open("ids.txt", "r") as f:
    ids = [ID(line.strip()) for line in f.readlines()]

Entrez.email = os.environ.get("EMAIL") or None
Entrez.api_key = os.environ.get("NCBI_API_KEY") or None


database = EuropePMC(storage = "./pdfs", figure_storage="./figures")
database.update_retry_strategy(Retry(total=2))

pdfs = database.get_pdfs(ids=ids)
