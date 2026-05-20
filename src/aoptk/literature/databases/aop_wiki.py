from SPARQLWrapper import JSON
from SPARQLWrapper import SPARQLWrapper
from aoptk.literature.abstract import Abstract
from aoptk.literature.get_abstract import GetAbstract
from aoptk.literature.id import ID


class AOPWiki(GetAbstract):
    """Class to extract data from AOP-Wiki."""

    endpoint_url = "https://aopwiki.rdf.bigcat-bioinformatics.org/sparql"
    prefix = """PREFIX aop: <http://aopkb.org/aop_ontology#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>"""
    abstract_query = (
        prefix
        + """

SELECT ?AOP ?AOPTitle ?abstract

WHERE {
  ?AOP a aop:AdverseOutcomePathway ;
    dc:title ?AOPTitle .
  OPTIONAL { ?AOP dcterms:abstract ?abstract. }
}
"""
    )

    def __init__(
        self,
    ):
        self.sparql = SPARQLWrapper(self.endpoint_url)
        self.sparql.setReturnFormat(JSON)

    def get_abstracts(self) -> list[Abstract]:
        """Get abstracts of AOPs from AOP-Wiki.

        Returns:
            list[Abstract]: List of abstracts.
        """
        self.sparql.setQuery(self.abstract_query)
        results = self.sparql.query().convert()

        abstracts: list[Abstract] = []
        for result in results["results"]["bindings"]:
            aop_id = result.get("AOP", {}).get("value")
            title = result.get("AOPTitle", {}).get("value", "")
            abstract = result.get("abstract", {}).get("value", "")
            text = f"{title}\n\n{abstract}".strip()
            abstracts.append(Abstract(id=ID(aop_id), text=text))

        return abstracts
