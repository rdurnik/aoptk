from metapub import FindIt

def is_europepmc_id(id: str) -> bool:
    if id.startswith("PMC"):
        return True
    return False

def get_pubmed_pdf_url(id) -> str:
    src = FindIt(id, retry_errors=True)
    return src.url