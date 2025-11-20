from aoptk.scispacy_find_chemical import ScispacyFindChemical
from aoptk.find_chemical import FindChemical

def test_can_create():
    actual = ScispacyFindChemical(None)
    assert actual is not None

def test_implements_interface():
    assert isinstance(ScispacyFindChemical(None), FindChemical)

def test_find_chemical_not_empty():
    actual = ScispacyFindChemical('').find_chemical()
    assert actual is not None

def test_find_chemical_one_sentence():
    sentence = ["Thioacetamide was studied for its effect on liver cells."]
    expected = "thioacetamide"
    actual = ScispacyFindChemical(sentence).scispacy_find_chemical()
    assert actual.chemical_name == expected