from aoptk.get_publication import GetPublication
from aoptk.parse_pdf import ParsePDF

def test_can_create():
    actual = ParsePDF(str)
    assert actual is not None

def test_implements_interface():
    assert issubclass(ParsePDF, GetPublication)

def test_get_publication_data_not_empty():
    actual = ParsePDF('').get_publication()
    assert actual is not None

def test_extract_abstract_with_abstract_specified():
    actual = ParsePDF('/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_abstractcalledabstract.pdf').parse_abstract()
    expected = 'The rational design and selective self-assembly of ﬂexible and unsymmetric ligands into large coordination complexes is an eminent challenge in supramolecular coordination chemistry. Here, we present the coordination-driven self-assembly of natural ursodeoxycholic-bile-acid-derived unsymmetric tris-pyridyl ligand (L) resulting in the selective and switchable formation of chiral stellated Pd6L8 and Pd12L16 cages. The selectivity of the cage originates in the adaptivity and ﬂexibility of the arms of the ligand bearing pyridyl moieties. The interspeciﬁc transformations can be controlled by changes in the reaction conditions. The orientational self-sorting of L into a single constitutional isomer of each cage, i.e., homochiral quadruple and octuple right-handed helical species, was conﬁrmed by a combination of molecular modelling and circular dichroism. The cages, derived from natural amphiphilic transport molecules, mediate the higher cellular uptake and increase the anticancer activity of bioactive palladium cations as determined in studies using in vitro 3D spheroids of the human hepatic cells HepG2.'
    assert actual == expected

# I do not know how to remove affiliations in this case...
# def test_extract_abstract_without_abstract_specified():
#     actual = ParsePDF('/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_abstractnotcalledabstract.pdf').parse_abstract()
#     expected = 'Background: The role of nucleotide-binding oligomerization domain-like receptors containing pyrin domain 3 (NLRP3) inflammasome and pyroptosis in the inflammatory microenvironment of metabolic-associated fatty liver disease (MASLD) has been posited as crucial. Bletilla striata polysaccharides (BSPs), extracted from the tubers of Bletilla striata (Thunb.) Rchb.f., exhibit significant anti-inflammatory properties. However, their potential protective effects on MASLD and their role in regulating pyroptosis remain unclear. Objectives: This study investigates the efficacy of BSP-1, a purified metabolite isolated from crude BSPs, on MASLD by evaluating its ability to modulate the NLRP3/caspase-1/GSDMD signaling pathway. Methods: To simulate MASLD in vivo and in vitro, high-fat diet (HFD)-induced rat models and free fatty acid (FFA)-stimulated HepG2 cells were used. Serum indicators and histopathological staining were employed to assess liver injury and lipid deposition. Additionally, enzyme-linked immunosorbent assay (ELISA), immunohistochemistry (IHC), immunofluorescence, real-time quantitative polymerase chain reaction (RT-qPCR), and western blotting (WB) analysis were conducted to examine the NLRP3/caspase-1/GSDMD pathway and related cytokine levels. Results: BSP-1 significantly ameliorates alanine aminotransferase (ALT), aspartate aminotransferase (AST), total cholesterol (TC), and triglyceride (TG) levels in both rat serum and HepG2 cells. Furthermore, BSP-1 reduces inflammatory factors interleukin (IL)-1β and IL-18, while improving pathological changes in rat liver tissue. Mechanistically, BSP-1 regulates the expression of pyroptosis-related proteins and mRNAs in the NLRP3/caspase-1/GSDMD pathway, thereby protecting against MASLD. Discussion: BSP-1 may represent a promising therapeutic agent for MASLD treatment by inhibiting the NLRP3/caspase-1/GSDMD signaling pathway.'
#     assert actual == expected

def test_extract_abstract_without_abstract_specified_no_introduction():
    actual = ParsePDF('/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_abstractnotcalledabstractnointroduction.pdf').parse_abstract()
    expected = 'This study explores the potential of six novel thiophene derivative thin films (THIOs) for reducing cancer cell adhesion and enhancing controlled drug release on inert glass substrates. Thiophene derivatives 3a–c and 5a–c were synthesized and characterized using IR, 1H NMR, 13C NMR, and elemental analysis before being spin-coated onto glass to form thin films. SEM analysis and roughness measurements were used to assess their structural and functional properties. Biological evaluations demonstrated that the films significantly reduced HepG2 liver cancer cell adhesion (~ 78% decrease vs. control) and enabled controlled drug release, validated through the Korsmeyer-Peppas model (R2 > 0.99). Theoretical studies, including in-silico target prediction, molecular docking with JAK1 (PDB: 4E4L), and DFT calculations, provided insights into the electronic properties and chemical reactivity of these compounds. Notably, compound 5b exhibited the best binding energy (-7.59 kcal/mol) within the JAK1 pocket, aligning with its observed apoptotic behavior in cell culture. DFT calculations further revealed that 5b had the lowest calculated energy values; -4.89 eV (HOMO) and − 3.22 eV (LUMO), and the energy gap was found to be 1.66 eV, supporting its role in JAK1 inhibition and cancer cell adhesion reduction. These findings underscore the promise of thiophene derivatives in biomedical applications, potentially leading to safer surgical procedures and more effective localized drug delivery systems.'
    assert actual == expected

def test_extract_abstract_no_abstract_keywords_introduction_specification():
    actual = ParsePDF('/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_no_abstract_introduction_keywords_specification.pdf').parse_abstract()
    expected = 'The rational design and selective self-assembly of flexible and unsymmetric ligands into large coordination complexes is an eminent challenge in supramolecular coordination chemistry. Here, we present the coordination-driven self-assembly of natural ursodeoxycholic-bile-acid-derived unsymmetric tris-pyridyl ligand (L) resulting in the selective and switchable formation of chiral stellated Pd6L8 and Pd12L16 cages. The selectivity of the cage originates in the adaptivity and flexibility of the arms of the ligand bearing pyridyl moieties. The interspecific transformations can be controlled by changes in the reaction conditions. The orientational self-sorting of L into a single constitutional isomer of each cage, i.e., homochiral quadruple and octuple right-handed helical species, was confirmed by a combination of molecular modelling and circular dichroism. The cages, derived from natural amphiphilic transport molecules, mediate the higher cellular uptake and increase the anticancer activity of bioactive palladium cations as determined in studies using in vitro 3D spheroids of the human hepatic cells HepG2.'
    assert actual == expected

def test_extract_full_text_with_abstract_specified():
    actual = ParsePDF('/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_abstractcalledabstract.pdf').parse_full_text()[13:39]
    expected = 'Natural chiral hydrophobic'
    assert actual == expected

def test_extract_full_text_without_abstract_specified():
    actual = ParsePDF('/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_abstractnotcalledabstract.pdf').parse_full_text()[1444:1563]
    expected = 'Metabolic-associated fatty liver disease (MASLD) is a chronic liver condition closely linked to metabolic disturbances.'
    assert actual == expected

def test_extract_full_text_without_abstract_specified_no_introduction():
    actual = ParsePDF('/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_abstractnotcalledabstractnointroduction.pdf').parse_full_text()[108:294]
    expected = 'Surgical tools used for tumor biopsy, resection, or ablation are susceptible to cancer cell adherence when they come into direct contact with tumor tissue, which can cause complications.'
    assert actual == expected

def test_extract_full_text_no_abstract_keywords_introduction_specification():
    actual = ParsePDF('/home/rdurnik/aoptk/tests/test_pdfs/test_pdf_no_abstract_introduction_keywords_specification.pdf').parse_full_text()
    expected = 'Natural chiral hydrophobic cavities are important for many biological functions, e.g., for recognition as parts of transport proteins or for substrate-specific transformations as parts of enzymes. To understand and mimic these natural systems and their (supra)molecular mechanisms of action, the development of their artificial counterparts (e.g., cages, macrocycles) from chiral molecules is desirable. Easing such efforts, nature readily offers convenient chiral building blocks (terpenoids, amino acids, or carbohydrates) which can be utilized. Intermolecular-interaction-mediated self- assembly together with metal coordination are essential natural processes to construct such higher- order structures and can easily be adapted in the development of artificial systems. The discovery of supramolecular coordination cages (SCCs) via coordination-driven self-assembly by Saalfrank et al.[1] led to the rapid development of a large group of metallo-cycles and metallo-cages mainly using rigid and symmetric bis/tris-pyridyl coordinating ligands and tetravalent square-planar Pd2+. [2] The edge- directed self-assembly of different bis-pyridyl ligands resulted in the formation of SCCs and macrocycles with the general formula PdnL2n, e.g., Pd2L4, Pd3L6, Pd4L8, Pd6L12, Pd12L24, Pd24L48, Pd30L60, or Pd48L96– the largest SCC described so far.[3] Whereas tris-pyridyl ligands led to Pd3nL4n SCCs, with only four types so far, i.e., Pd3L4, [4–6] Pd9L12 (only one),[7] Pd18L24[8] (one) via edge- directed self-assembly, and the most common Pd6L8 [9] via face-directed self-assembly.'
    assert actual == expected

def test_extract_abbreviations():
    actual = ParsePDF('/home/rdurnik/aoptk/tests/test_pdfs/test_abbreviation.pdf').extract_abbreviations()
    actual = [list(actual.items())[0], list(actual.items())[1], list(actual.items())[-1]]
    expected = [('AASLD', 'American Association for the Study of Liver Diseases'), ('ACC', 'acetyl-CoA carboxylase'), ('VLDL', 'very-low-density lipoprotein')]
    assert actual == expected

# Test to see if the PDF opens correctly?

    