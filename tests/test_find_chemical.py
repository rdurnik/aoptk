from aoptk.find_chemical import FindChemicalStub
from aoptk.interfaces import IFindChemical


def test_can_create():
    actual = FindChemicalStub()
    assert actual is not None

def test_implements_interface():
    assert issubclass(FindChemicalStub, IFindChemical)

def test_find_chemical_not_empty():
    actual = FindChemicalStub().find_chemical("", "")
    assert actual is not None

def test_find_chemical_in_sentence():
    actual = FindChemicalStub().find_chemical("Methanol", "Methanol is a very dangerous chemical.")
    assert actual == "Methanol"

def test_find_chemical_in_sentence_different_writing():
    actual = FindChemicalStub().find_chemical("Methanol", "CH3OH (methanol) is a very dangerous chemical.")
    assert actual == "Methanol"

def test_chemical_not_in_sentence():
    actual = FindChemicalStub().find_chemical("Ethanol", "Methanol is a very dangerous chemical.")
    assert actual is None

def test_find_chemical_unspecified():
    actual = FindChemicalStub().find_chemical_unspecified("Methanol is a very dangerous chemical.")
    assert actual == "Methanol"

def test_with_more_data():
    chemicals = ["Ethanol", "Methanol"]
    sentences = [
        "While Ethanol is known as good alcohol, Methanol will make you blind.",
        "Don't drink too much Methanol.",
        "Neither too much Ethanol."
    ]

    sut = FindChemicalStub()

    actual = []
    for c in chemicals:
        for s in sentences:
            result = sut.find_chemical(c,s)
            if result is not None:
                actual.append(result)
    
    assert actual == ["Ethanol", "Ethanol", "Methanol", "Methanol"]
