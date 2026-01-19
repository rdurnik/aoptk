from xml.etree import ElementTree as ET
import requests
from requests import HTTPError


def is_europepmc_id(publication_id: str) -> bool:
    """Check if the given publication ID is a EuropePMC ID."""
    return bool(publication_id.startswith("PMC"))


def get_pubmed_pdf_url(publication_id: str) -> str:
    """Get the PubMed PDF URL for a given publication ID.
    
    This function attempts to find a PDF URL for a given PubMed ID by:
    1. Fetching article metadata from NCBI E-utilities API
    2. Extracting the DOI and/or PMC ID
    3. Attempting to construct a PDF URL from available metadata
    
    Args:
        publication_id: The PubMed ID (PMID) to look up
        
    Returns:
        str: A URL to the PDF if found
        
    Raises:
        HTTPError: If no URL could be found or if the API request failed
    """
    # Fetch article metadata from NCBI E-utilities
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": publication_id,
        "retmode": "xml"
    }
    
    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPError(f"Failed to fetch article metadata: {e}")
    
    # Parse XML response
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        raise HTTPError(f"Failed to parse article metadata: {e}")
    
    # Find the PubmedArticle element
    article = root.find(".//PubmedArticle")
    if article is None:
        raise HTTPError(f"No article found for PMID {publication_id}")
    
    # Extract DOI and PMC ID
    doi = None
    pmc = None
    for article_id in article.findall(".//ArticleId"):
        id_type = article_id.get("IdType")
        if id_type == "doi":
            doi = article_id.text
        elif id_type == "pmc":
            pmc = article_id.text
    
    # If we have a PMC ID, use EuropePMC
    if pmc:
        return f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={pmc}&blobtype=pdf"
    
    # If we have a DOI, try using it through doi.org
    # Note: This may not always lead to a direct PDF, but it's a reasonable attempt
    if doi:
        # Use NCBI's linkout service which can resolve to publisher PDFs
        linkout_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={publication_id}&format=json"
        try:
            linkout_response = requests.get(linkout_url, timeout=10)
            linkout_response.raise_for_status()
            linkout_data = linkout_response.json()
            
            # Check if there's a PMC ID in the response
            if "records" in linkout_data and len(linkout_data["records"]) > 0:
                record = linkout_data["records"][0]
                if "pmcid" in record:
                    pmc_from_linkout = record["pmcid"]
                    return f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={pmc_from_linkout}&blobtype=pdf"
        except (requests.RequestException, ValueError, KeyError):
            # If linkout service fails, fall through to DOI-based URL
            pass
        
        # As a last resort, return the DOI URL (may redirect to publisher page)
        return f"https://doi.org/{doi}"
    
    # If we couldn't find any way to get the PDF, raise an error
    raise HTTPError(f"No DOI or PMC ID found for PMID {publication_id}")
