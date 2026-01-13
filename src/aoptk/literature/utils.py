from metapub import FindIt
from requests import HTTPError


def is_europepmc_id(publication_id: str) -> bool:
    """Check if the given publication ID is a EuropePMC ID."""
    return bool(publication_id.startswith("PMC"))


def get_pubmed_pdf_url(publication_id: str) -> str:
    """Get the PubMed PDF URL for a given publication ID."""
    findit = FindIt(publication_id, retry_errors=True, max_redirects=10, verify=False, request_timeout=20)
    if not findit.url:
        raise HTTPError(findit.reason)
    return findit.url
