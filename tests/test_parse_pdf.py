import os
import shutil
import pytest
from aoptk.get_publication import GetPublication
from aoptk.pymupdf_parser import PymupdfParser
from aoptk.pdf import PDF


def test_can_create():
    actual = PymupdfParser(str)
    assert actual is not None

def test_implements_interface():
    assert issubclass(PymupdfParser, GetPublication)

def test_get_publication_data_not_empty():
    actual = PymupdfParser("").get_publications()
    assert actual is not None

# Make the PDFs into fixtures that are downloaded from Europe PMC and deleted.
# Will sometimes extract irrelevant parts such as authors, affiliations...
@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_abstractcalledabstract.pdf", "The rational design and selective self-assembly of ﬂexible and unsymmetric ligands into large coordination complexes is an eminent challenge in supramolecular coordination chemistry. Here, we present the coordination-driven self-assembly of natural ursodeoxycholic-bile-acid-derived unsymmetric tris-pyridyl ligand (L) resulting in the selective and switchable formation of chiral stellated Pd6L8 and Pd12L16 cages. The selectivity of the cage originates in the adaptivity and ﬂexibility of the arms of the ligand bearing pyridyl moieties. The interspeciﬁc transformations can be controlled by changes in the reaction conditions. The orientational self-sorting of L into a single constitutional isomer of each cage, i.e., homochiral quadruple and octuple right-handed helical species, was conﬁrmed by a combination of molecular modelling and circular dichroism. The cages, derived from natural amphiphilic transport molecules, mediate the higher cellular uptake and increase the anticancer activity of bioactive palladium cations as determined in studies using in vitro 3D spheroids of the human hepatic cells HepG2."),
        ("/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_abstractnotcalledabstractnointroduction.pdf", "This study explores the potential of six novel thiophene derivative thin films (THIOs) for reducing cancer cell adhesion and enhancing controlled drug release on inert glass substrates. Thiophene derivatives 3a–c and 5a–c were synthesized and characterized using IR, 1H NMR, 13C NMR, and elemental analysis before being spin-coated onto glass to form thin films. SEM analysis and roughness measurements were used to assess their structural and functional properties. Biological evaluations demonstrated that the films significantly reduced HepG2 liver cancer cell adhesion (~ 78% decrease vs. control) and enabled controlled drug release, validated through the Korsmeyer-Peppas model (R2 > 0.99). Theoretical studies, including in-silico target prediction, molecular docking with JAK1 (PDB: 4E4L), and DFT calculations, provided insights into the electronic properties and chemical reactivity of these compounds. Notably, compound 5b exhibited the best binding energy (-7.59 kcal/mol) within the JAK1 pocket, aligning with its observed apoptotic behavior in cell culture. DFT calculations further revealed that 5b had the lowest calculated energy values; -4.89 eV (HOMO) and − 3.22 eV (LUMO), and the energy gap was found to be 1.66 eV, supporting its role in JAK1 inhibition and cancer cell adhesion reduction. These findings underscore the promise of thiophene derivatives in biomedical applications, potentially leading to safer surgical procedures and more effective localized drug delivery systems."),
        ("/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_no_abstract_introduction_keywords_specification.pdf", "The rational design and selective self-assembly of flexible and unsymmetric ligands into large coordination complexes is an eminent challenge in supramolecular coordination chemistry. Here, we present the coordination-driven self-assembly of natural ursodeoxycholic-bile-acid-derived unsymmetric tris-pyridyl ligand (L) resulting in the selective and switchable formation of chiral stellated Pd6L8 and Pd12L16 cages. The selectivity of the cage originates in the adaptivity and flexibility of the arms of the ligand bearing pyridyl moieties. The interspecific transformations can be controlled by changes in the reaction conditions. The orientational self-sorting of L into a single constitutional isomer of each cage, i.e., homochiral quadruple and octuple right-handed helical species, was confirmed by a combination of molecular modelling and circular dichroism. The cages, derived from natural amphiphilic transport molecules, mediate the higher cellular uptake and increase the anticancer activity of bioactive palladium cations as determined in studies using in vitro 3D spheroids of the human hepatic cells HepG2."),

    ],
)
def test_extract_abstract(path, expected):
    actual = PymupdfParser([PDF(path)]).get_publications()[0].abstract
    assert actual == expected

# Will extract irrelevant parts such as list of keywords, /n, etc...
@pytest.mark.parametrize(
    ("path", "where", "expected"),
    [
        ("/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_abstractcalledabstract.pdf", slice(13, 39), "Natural chiral hydrophobic"),
        ("/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_abstractnotcalledabstract.pdf", slice(1444, 1484), "Metabolic-associated fatty liver disease"),
        ("/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_abstractnotcalledabstractnointroduction.pdf", slice(108, 127), "Surgical tools used"),
        ("/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_no_abstract_introduction_keywords_specification.pdf", slice(0, 26), "Natural chiral hydrophobic"),
    ],
)
def test_extract_full_text(path, where, expected):
    actual = PymupdfParser([PDF(path)]).get_publications()[0].full_text[where]
    assert actual == expected


def test_extract_abbreviations_with_content():
    abbrev_dict = PymupdfParser([PDF("/home/rdurnik/aoptk/tests/test_pdfs/test_abbreviation.pdf")]).get_publications()[0].abbreviations
    actual = [list(abbrev_dict.items())[0], list(abbrev_dict.items())[1], list(abbrev_dict.items())[-1]]
    expected = [("AASLD", "American Association for the Study of Liver Diseases"), ("ACC", "acetyl-CoA carboxylase"), ("VLDL", "very-low-density lipoprotein")]
    assert actual == expected

def test_extract_abbreviations_empty():
    abbrev_dict = PymupdfParser([PDF("/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_abstractnotcalledabstract.pdf")]).get_publications()[0].abbreviations
    assert abbrev_dict == {}

def test_extract_id():
    actual = PymupdfParser([PDF("/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_abstractcalledabstract.pdf")]).get_publications()[0].id
    expected = "test_pdf_abstractcalledabstract.pdf"
    assert actual == expected

# def test_extract_figures():
#     actual = PymupdfParser([PDF("/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_abstractcalledabstract.pdf")]).get_publications()[0].figures
#     folder = "/home/rdurnik/aoptk/tests/figure_storage"
#     assert os.path.isdir(folder)
#     folder_size = sum(
#         os.path.getsize(os.path.join(root, f))
#         for root, _, files in os.walk(folder)
#         for f in files
#     )
#     assert folder_size == 2500066
#     assert len(actual) == 5

#     shutil.rmtree(folder, ignore_errors=True)

def test_extract_figure_description():
    actual = PymupdfParser([PDF("/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_abstractcalledabstract.pdf")]).get_publications()[0].figure_descriptions
    expected = ["Figure 5. Toxicological studies of the SCCs. a) Concentration-response of HepG2 spheroid viability (ATP content) after 8 days of exposure to Pd(NO3)2, L, Pd6L8, and Pd12L16. The asterisk (*) indicates a statistically signiﬁcant (P < 0.05) diﬀerence from the solvent control. b) Relation of spheroid viability to palladium content measured in spheroids. ρ represents Spearman’s rank correlation coeﬃcient with a P value."]
    assert len(actual) == 5
    assert actual[-1:] == expected

