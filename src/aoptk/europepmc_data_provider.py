from aoptk.get_publication_data import GetPublicationData
import pandas as pd
import requests
from metapub import FindIt
import os

# Add a way to remove review articles: Simply add TITLE_ABS:(query). Probably by having two types of get_id_list?
# What if the user only wants to search through abstracts? PDF is not needed in that case.

class GetEuropePMCPublicationData(GetPublicationData):
    def __init__(self, query: str):
        self._query = query

    def get_publication_data(self):
        id_list = self.get_id_list()
        for id in id_list:
            if self.is_europepmc_id(id): # All PMC IDs start with PMC. It seems that only publications with PMC ID are in the Europe PMC open access subset.
                try:
                    self.get_europepmc_pdf(id)
                except Exception as e:
                    self.get_europepmc_json(id) # If PDF is not available, at least get the abstract?
                    continue
            else: # If the PDF is not available in Europe PMC, it could still be accessible via PubMed (small fraction of papers, most likely).
                try:
                    self.get_pubmed_pdf(id)
                except Exception as e:
                    self.get_europepmc_json(id) # If PDF is not available, at least get the abstract?
                    continue
        return '' # ???
    
    def is_europepmc_id(self, id):
        if id.startswith("PMC"):
            return True
        return False
    
    def get_id_list(self):
        page_size = 1000
        cursor_mark = "*"
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        id_list = []
        while True:
            params = {
                "query": self._query,
                "format": "json",
                "pageSize": page_size,
                "cursorMark": cursor_mark,
                "resultType": "idlist"
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data_europepmc = response.json()
            results = data_europepmc.get("resultList", {}).get("result", [])
            
            for result in results:
                publication_id = result.get("pmcid") or result.get("pmid") or result.get("id")
                if publication_id:
                    id_list.append(publication_id)
            
            if len(results) < page_size or not data_europepmc.get("nextCursorMark") or data_europepmc["nextCursorMark"] == cursor_mark:
                break
            cursor_mark = data_europepmc["nextCursorMark"]
        return id_list
    
    def get_europepmc_pdf(self, id):
        response = requests.get(f'https://europepmc.org/backend/ptpmcrender.fcgi?accid={id}&blobtype=pdf', stream=True)
        response.raise_for_status()
        filename = f'{id}.pdf'
        os.makedirs('tests/pdf_storage', exist_ok=True)
        filepath = os.path.join('tests/pdf_storage', filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    def get_pubmed_pdf(self, id):
        pdf_url = self.get_pubmed_pdf_url(id)
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()
        filename = f'{id}.pdf'
        os.makedirs('tests/pdf_storage', exist_ok=True)
        filepath = os.path.join('tests/pdf_storage', filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    def get_pubmed_pdf_url(self, id):
        src = FindIt(id, retry_errors=True)
        pdf_url = src.url or ''
        return pdf_url
    
    def get_europepmc_json(self, id):
        page_size = 1000
        cursor_mark = "*"
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        while True:
            params = {
                "query": id, # One could also put a real query here (e.g., 'HepG2 thioacetamide'). But passing the ID of a publication will find the publication.
                "format": "json",
                "pageSize": page_size,
                "cursorMark": cursor_mark,
                "resultType": "core"
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            json = response.json() # Only return JSON and do the parsing in a different module?
            results = json.get("resultList", {}).get("result", [])
            for record in results:
                abstract = record.get("abstractText", "")
            return abstract


