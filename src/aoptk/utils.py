from metapub import FindIt


def is_europepmc_id(publication_id: str) -> bool:
    """Check if the given publication ID is a EuropePMC ID."""
    return bool(publication_id.startswith("PMC"))


def get_pubmed_pdf_url(publication_id: str) -> str:
    """Get the PubMed PDF URL for a given publication ID."""
    return FindIt(publication_id, retry_errors=True, max_redirects = 5, verify=False).url
