def is_europepmc_id(publication_id: str) -> bool:
    """Check if the given publication ID is a EuropePMC ID."""
    return bool(publication_id.startswith("PMC"))
