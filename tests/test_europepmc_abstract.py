from aoptk.europepmc_abstract import EuropePMCAbstract
from aoptk.get_abstract import GetAbstract


def test_can_create():
    """Can create EuropePMCAbstract instance."""
    actual = EuropePMCAbstract(str)
    assert actual is not None


def test_implements_interface():
    """EuropePMCAbstract implements GetAbstract interface."""
    assert issubclass(EuropePMCAbstract, GetAbstract)


def test_get_abstract_not_empty():
    """Get abstracts returns non-empty list."""
    actual = EuropePMCAbstract("").get_abstracts()
    assert actual is not None


def test_generate_abstract_for_given_query():
    """Generate abstract for given query."""
    query = "TITLE_ABS:(liver cancer AND hepg2 AND thioacetamide) AND (FIRST_PDATE:[2018 TO 2019])"
    actual = EuropePMCAbstract(query).get_abstracts()[0].text[:96]
    expected = "Insulin growth factor (IGF) family and their receptors play a great role in tumors' development."
    assert actual == expected
