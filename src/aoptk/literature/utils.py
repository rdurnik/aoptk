from xml.etree import ElementTree as ET
import requests
from requests import HTTPError

# Tool and contact information for NCBI API requests
_TOOL_NAME = "aoptk"
_CONTACT_EMAIL = "support@aoptk.org"
_PROJECT_URL = "https://github.com/rdurnik/aoptk"

# Try to get version from package, fallback to a default if not available
try:
    from aoptk import __version__
except ImportError:
    __version__ = "unknown"

_USER_AGENT = f"{_TOOL_NAME}/{__version__} ({_PROJECT_URL}; mailto:{_CONTACT_EMAIL})"


def is_europepmc_id(publication_id: str) -> bool:
    """Check if the given publication ID is an EuropePMC ID."""
    return bool(publication_id.startswith("PMC"))


def _fetch_article_metadata(publication_id: str) -> ET.Element:
    """Fetch article metadata from NCBI E-utilities API.

    Args:
        publication_id: The PubMed ID (PMID) to look up

    Returns:
        ET.Element: The root element of the parsed XML response

    Raises:
        HTTPError: If the API request fails or response cannot be parsed
    """
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": publication_id,
        "retmode": "xml",
        "tool": _TOOL_NAME,
        "email": _CONTACT_EMAIL,
    }
    headers = {
        "User-Agent": _USER_AGENT,
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.RequestException as e:
        msg = f"Failed to fetch article metadata: {e}"
        raise HTTPError(msg) from e

    try:
        return ET.fromstring(response.content)
    except ET.ParseError as e:
        msg = f"Failed to parse article metadata: {e}"
        raise HTTPError(msg) from e


def _try_linkout_service(publication_id: str) -> str | None:
    """Try to get PMC ID from NCBI linkout service.

    Args:
        publication_id: The PubMed ID (PMID) to look up

    Returns:
        str | None: EuropePMC URL if PMC ID found, None otherwise
    """
    linkout_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={publication_id}&format=json"
    headers = {
        "User-Agent": _USER_AGENT,
    }

    try:
        linkout_response = requests.get(linkout_url, headers=headers, timeout=10)
        linkout_response.raise_for_status()
        linkout_data = linkout_response.json()

        records = linkout_data.get("records", [])
        if records:
            record = records[0]
            if "pmcid" in record:
                pmc_from_linkout = record["pmcid"]
                return f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={pmc_from_linkout}&blobtype=pdf"
    except (requests.RequestException, ValueError):
        # If linkout service fails or returns invalid JSON, return None
        # This is expected for articles not in PMC
        pass
    return None


def _construct_publisher_pdf_url(doi: str, _article: ET.Element) -> str | None:  # noqa: PLR0911
    """Attempt to construct a publisher-specific PDF URL from DOI and article metadata.

    Args:
        doi: The DOI of the article
        _article: The PubmedArticle XML element (reserved for future use)

    Returns:
        str | None: Publisher-specific PDF URL if constructable, None otherwise
    """
    if not doi:
        return None

    # Try De Gruyter pattern (works for many publishers)
    if "10.1515/" in doi:
        return f"https://www.degruyter.com/document/doi/{doi}/pdf"

    # Try BMJ pattern
    if "10.1136/" in doi:
        # For gut.bmj.com, try the pattern with doi suffix
        doi_suffix = doi.split("/")[-1] if "/" in doi else doi
        return f"https://gut.bmj.com/content/gutjnl/{doi_suffix}.full.pdf"

    # Try Elsevier/ScienceDirect pattern
    if "10.1016/" in doi:
        return f"https://www.sciencedirect.com/science/article/pii/{doi.split('/')[-1]}/pdfft"

    # Try Wiley pattern
    if "10.1002/" in doi or "10.1111/" in doi:
        return f"https://onlinelibrary.wiley.com/doi/pdfdirect/{doi}"

    # Try Springer pattern
    if "10.1007/" in doi:
        return f"https://link.springer.com/content/pdf/{doi}.pdf"

    # Try Nature pattern
    if "10.1038/" in doi:
        return f"https://www.nature.com/articles/{doi.split('/')[-1]}.pdf"

    # Try Oxford Academic pattern
    if "10.1093/" in doi:
        return f"https://academic.oup.com/pdfaccess/article/{doi}/pdf"

    return None


def get_pubmed_pdf_url(publication_id: str) -> str:
    """Get the PubMed PDF URL for a given publication ID.

    This function attempts to find a PDF URL for a given PubMed ID by:
    1. Fetching article metadata from NCBI E-utilities API
    2. Extracting the DOI and/or PMC ID
    3. Attempting to construct a publisher-specific PDF URL from available metadata

    Args:
        publication_id: The PubMed ID (PMID) to look up

    Returns:
        str: A URL to the PDF if found

    Raises:
        HTTPError: If no URL could be found or if the API request failed
    """
    root = _fetch_article_metadata(publication_id)

    # Find the PubmedArticle element
    article = root.find(".//PubmedArticle")
    if article is None:
        msg = f"No article found for PMID {publication_id}"
        raise HTTPError(msg)

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

    # Try NCBI's linkout service to find a PMC ID
    linkout_url = _try_linkout_service(publication_id)
    if linkout_url:
        return linkout_url

    # Try to construct publisher-specific PDF URL
    if doi:
        publisher_url = _construct_publisher_pdf_url(doi, article)
        if publisher_url:
            return publisher_url

        # Fallback to DOI URL as last resort
        return f"https://doi.org/{doi}"

    # If we couldn't find any way to get the PDF, raise an error
    msg = f"No DOI or PMC ID found for PMID {publication_id}"
    raise HTTPError(msg)
