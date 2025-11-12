from aoptk.interfaces import IFindChemical


class FindChemicalStub(IFindChemical):
    def __init__(self):
        pass

    def find_chemical(self, chemical, sentence):
        return chemical if chemical in sentence else None
    
    def find_chemical_unspecified(self, sentence):
        return None