import os
from typing import Optional
from urllib import response
import requests
from aoptk.get_pdf import GetPDF
from aoptk.pdf import PDF
from aoptk.utils import get_pubmed_pdf_url, is_europepmc_id


class EuropePMC(GetPDF):
    def __init__(self, query: str, storage: str = "tests/pdf_storage"):
        self._query = query
        self.storage = storage
        os.makedirs(self.storage, exist_ok=True)

        self.id_list = self.get_id_list()

    def pdfs(self) -> list[PDF]:
        pdf_list = []
        for id in self.id_list:
            pdf_list.append(self.get_pdf(id))
        pdf_list = [pdf for pdf in pdf_list if pdf is not None]
        return pdf_list

    def get_id_list(self) -> list[str]:
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
                "resultType": "idlist",
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data_europepmc = response.json()
            results = data_europepmc.get("resultList", {}).get("result", [])

            for result in results:
                publication_id = result.get("pmcid") or result.get("pmid") or result.get("id")
                if publication_id:
                    id_list.append(publication_id)

            next_cursor = data_europepmc.get("nextCursorMark")
            if not next_cursor or next_cursor == cursor_mark:
                break
            cursor_mark = next_cursor
        return id_list

    def remove_reviews(self):
        self._query += ' NOT PUB_TYPE:"Review"'
        return self

    def abstracts_only(self):
        self._query = "ABSTRACT:(" + self._query + ")"
        return self

    def get_pdf(self, id) -> Optional[PDF]:
        response = requests.get(f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={id}&blobtype=pdf", stream=True)
        if not response.ok:
            pubmed_url = get_pubmed_pdf_url(id)
            if pubmed_url:
                response = requests.get(pubmed_url, stream=True)
                if not response.ok:
                    return None
       
        return self.write(id, response)

    def write(self, id, response) -> PDF:
        filepath = os.path.join(self.storage, f"{id}.pdf")
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return PDF(filepath)
