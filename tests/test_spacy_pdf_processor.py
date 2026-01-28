from __future__ import annotations
import shutil
from pathlib import Path
import pandas as pd
import pytest
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.literature.id import ID
from aoptk.literature.pdf import PDF
from aoptk.literature.pymupdf_parser import PymupdfParser
from aoptk.spacy_pdf_processor import SpacyPDF

output_dir = "/home/rdurnik/aoptk/tests/figure_storage"


def test_can_create():
    """Can create SpacyPDF instance."""
    actual = SpacyPDF([])
    assert actual is not None


def test_implements_pymupdfparser():
    """SpacyPDF implements PymupdfParser interface."""
    assert issubclass(SpacyPDF, PymupdfParser)


def test_get_publications_not_empty():
    """Test that get_publications method returns a non-empty result."""
    actual = SpacyPDF([PDF("tests/test_pdfs/test_pdf.pdf")]).get_publications()
    assert actual is not None


@pytest.fixture(
    params=[
        {
            "id": "PMC12416454",
            "paragraph_number": 15,
            "full_text": "More than three decades after the first discovery, "
            "most of these metallo-supramolecular complexes are achiral and "
            "symmetric. Several approaches have been employed to construct "
            "low-symmetry, unsymmetric, or chiral coordination complexes using "
            "unsymmetric bidentate ligands, [10] a combination of multiple "
            "symmetric ligands (heteroleptic complexes), [11,12] or even "
            "single-type symmetric ligands. [13-16] However, unlike natural "
            "systems, the presence of stereogenic carbons in the structure "
            "of ligands is rare, mostly limited to the peripheral areas of "
            "ligands and their resulting complexes, [17] e.g., using peptides,"
            " [18,19] pentasaccharide, [20] or short alkyl chains. [21]",
        },
        {
            "id": "PMC12638863",
            "paragraph_number": 35,
            "full_text": "In  our  previous  paper  we  shed  light  on  the  impact "
            " of  cellular  respiration  altering  the  mitochondrial temperature  in"
            "  both  health  and  disease 35 .  Moreover,  recent  studies  reported "
            " that  Warburg  effect  in  HCC affect the mitochondrial temperature 38,39"
            " .  Hernin, we investigated the impact of this metabolic switch on the "
            "mitochondrial temperature in HCC. Cancer cells were treated with metformin"
            " to suppress glycolysis to emulate lower metabolically active cancer cells.",
        },
    ],
)
def provide_params_extract_full_text_fixture(request: pytest.FixtureRequest):
    """Provide parameters for extract full text fixture."""
    europepmc = EuropePMC(request.param["id"])
    data = {
        "europepmc": europepmc,
        "paragraph_number": request.param["paragraph_number"],
        "full_text": request.param["full_text"],
    }
    yield data
    if Path(europepmc.storage).exists():
        shutil.rmtree(europepmc.storage)


def test_extract_full_text_europepmc(provide_params_extract_full_text_fixture: dict):
    """Test extracting full text from EuropePMC PDFs."""
    actual = (
        SpacyPDF(provide_params_extract_full_text_fixture["europepmc"].pdfs())
        .get_publications()[0]
        .full_text[provide_params_extract_full_text_fixture["paragraph_number"]]
    )
    assert actual == provide_params_extract_full_text_fixture["full_text"]
    if Path(output_dir).exists():
        shutil.rmtree(output_dir)


@pytest.mark.parametrize(
    ("potential_footer_header", "output"),
    [
        (
            "doi.org/10.1002/anie.202513902",
            True,
        ),
        (
            "Durnik et al.",
            True,
        ),
        (
            "HepG2 cells were used in this study.",
            False,
        ),
    ],
)
def test_is_page_header_footer(potential_footer_header: str, output: bool):
    """Test identifying page headers and footers."""
    actual = SpacyPDF([])._is_page_header_footer(text=potential_footer_header)  # noqa: SLF001
    assert actual == output


@pytest.mark.parametrize(
    ("potential_formatting", "output"),
    [
        (
            "GLYPH<c=20,font=/HTQHQB+TimesNewRomanPS-ItalicMT"
            ">GLYPH<c=20,font=/HTQHQB+TimesNewRomanPS-ItalicMT"
            ">GLYPH<c=19,font=/HTQHQB+TimesNewRomanPS-ItalicMT"
            ">GLYPH<c=25,font=/HTQHQB+TimesNewRomanPS-ItalicMT"
            ">GLYPH<c=26,font=/HTQHQB+TimesNewRomanPS-ItalicMT"
            ">GLYPH<c=28,font=/HTQHQB+TimesNewRomanPS-ItalicMT>",
            True,
        ),
        (
            "This is normal text without any artifacts.",
            False,
        ),
    ],
)
def test_is_formatting(potential_formatting: str, output: bool):
    """Test identifying formatting artifacts."""
    actual = SpacyPDF([])._is_formatting(text=potential_formatting)  # noqa: SLF001
    assert actual == output


@pytest.mark.parametrize(
    ("text_with_terminator", "output"),
    [
        (
            "This is a complete sentence.",
            True,
        ),
        (
            "Is this a question?",
            True,
        ),
        (
            "What an exclamation!",
            True,
        ),
        (
            "This sentence has no terminator",
            False,
        ),
        (
            "Sentence with trailing spaces.   ",
            True,
        ),
        (
            "A sentence but there is a reference at the end. [12]",
            True,
        ),
        (
            "A sentence but there is a reference at the end 12,13.",
            True,
        ),
    ],
)
def test_ends_with_sentence_terminator(text_with_terminator: str, output: bool):
    """Test identifying text ending with sentence terminators."""
    actual = SpacyPDF([])._ends_with_sentence_terminator(text=text_with_terminator)  # noqa: SLF001
    assert actual == output


@pytest.mark.parametrize(
    ("text_with_digit", "output"),
    [
        (
            "Published in 2024",
            True,
        ),
        (
            "Published in 2024.",
            False,
        ),
        (
            "A sentence but there is a reference at the end. 12,13",
            True,
        ),
    ],
)
def test_has_digit_at_the_end(text_with_digit: str, output: bool):
    """Test identifying text ending with sentence terminators."""
    actual = SpacyPDF([])._has_digit_at_the_end(text=text_with_digit)  # noqa: SLF001
    assert actual == output


@pytest.fixture(
    params=[
        {
            "id": ID("PMC12416454"),
            "expected_abstract": "Abstract: The rational design and "
            "selective self-assembly of flexible and unsymmetric ligands"
            " into large coordination complexes is an eminent challenge "
            "in supramolecular coordination chemistry. Here, we present "
            "the coordination-driven self-assembly of natural "
            "ursodeoxycholic-bile-acid-derived unsymmetric tris -pyridyl "
            "ligand ( L ) resulting in the selective and switchable formation "
            "of chiral stellated Pd6 L 8 and Pd12 L 16 cages. The selectivity"
            " of the cage originates in the adaptivity and flexibility of "
            "the arms of the ligand bearing pyridyl moieties. The "
            "interspecific transformations can be controlled by changes"
            " in the reaction conditions. The orientational self-sorting "
            "of L into a single constitutional isomer of each cage, i.e., "
            "homochiral quadruple and octuple right-handed helical species, "
            "was confirmed by a combination of molecular modelling and circular "
            "dichroism. The cages, derived from natural amphiphilic "
            "transport molecules, mediate the higher cellular uptake "
            "and increase the anticancer activity of bioactive palladium "
            "cations as determined in studies using in vitro 3D spheroids"
            " of the human hepatic cells HepG2.",
        },
        {
            "id": ID("PMC12181427"),
            "expected_abstract": "This study explores the potential of "
            "six novel thiophene derivative thin films (THIOs) for reducing"
            " cancer cell adhesion and enhancing controlled drug release on"
            " inert glass substrates. Thiophene derivatives 3a-c and 5a-c"
            " were synthesized and characterized using IR,  1 H NMR, 13"
            " C NMR, and elemental analysis before being spin-coated "
            "onto glass to form thin films. SEM analysis and roughness"
            " measurements were used to assess their structural and "
            "functional properties. Biological evaluations demonstrated"
            " that the films significantly reduced HepG2 liver cancer "
            "cell adhesion (~ 78% decrease vs. control) and enabled "
            "controlled drug release, validated through the Korsmeyer-Peppas "
            "model (R 2 > 0.99). Theoretical studies, including "
            "in-silico target prediction, molecular docking with "
            "JAK1 (PDB: 4E4L), and DFT calculations, provided insights"
            " into the electronic properties and chemical reactivity of"
            " these compounds. Notably, compound 5b exhibited the best "
            "binding energy (-7.59 kcal/mol) within the JAK1 pocket, "
            "aligning with its observed apoptotic behavior in cell "
            "culture. DFT calculations further revealed that 5b had "
            "the lowest calculated energy values; -4.89 eV (HOMO) "
            "and - 3.22 eV (LUMO), and the energy gap was found to "
            "be 1.66 eV, supporting its role in JAK1 inhibition and "
            "cancer cell adhesion reduction. These findings underscore "
            "the promise of thiophene derivatives in biomedical "
            "applications, potentially leading to safer surgical "
            "procedures and more effective localized drug delivery systems.",
        },
        {
            "id": ID("PMC12805873"),
            "expected_abstract": "Abstract. Liver cancer is a highly aggressive "
            "cancer and the regulatory roles of microRNAs (miRs) in its progression "
            "are still being explored. miR-448, which is implicated in several types "
            "of cancer, remains to be fully characterized in liver cancer, "
            "particularly regarding its presence in exosomes. The aim of the "
            "present study was to examine the effects of exosomal miR-448 "
            "(EXO-miR-448) on liver cancer cell behavior. The expression levels "
            "of miR-448 in human liver cancer cell lines and its localization in "
            "exosomes were analyzed using reverse transcription-quantitative PCR, "
            "transmission electron microscopy and nanoparticle tracking analysis, "
            "with western blotting performed to detect exosomal markers. Functional "
            "assays were conducted to assess the effects of EXO-miR-448 on cell "
            "proliferation, migration and invasion. The results demonstrated that"
            " miR-448 expression was significantly downregulated in human liver "
            "cancer cell lines (HepG2, Hep3B and SK-HEP-1) compared  with  that  "
            "in  normal  liver  cells.  Furthermore, exosomal analysis confirmed "
            "that miR-448 was enriched within exosomes rather than being secreted "
            "into the supernatant. EXO-miR-448 also inhibited liver cancer cell"
            " proliferation, migration and invasion, as demonstrated using Cell"
            " Counting Kit-8 and Transwell assays. Bioinformatics and functional"
            " assays further identified Ras-related protein Rab-7a (RAB7A) as a "
            "direct downstream target of miR-448, with its overexpression rescuing "
            "the inhibitory effects of EXO-miR-448 on cell behavior. Furthermore, "
            "EXO-miR-448 suppressed glycolysis in liver cancer cells by targeting "
            "RAB7A, as indicated by reduced lactate production, glucose uptake, ATP"
            " levels and extracellular acidification rate. In conclusion, "
            "EXO-miR-448 inhibits liver cancer cell proliferation, migration,"
            " invasion and glycolysis by targeting RAB7A. These findings "
            "underscore the importance of miR-448 in liver cancer biology "
            "and support its further evaluation in future translational studies.",
        },
    ],
)
def provide_params_extract_abstract_fixture(request: pytest.FixtureRequest):
    """Provide parameters for extract abstract fixture."""
    europepmc = EuropePMC(request.param["id"])
    data = {
        "europepmc": europepmc,
        "expected_abstract": request.param["expected_abstract"],
    }
    yield data
    if Path(europepmc.storage).exists():
        shutil.rmtree(europepmc.storage)


def test_extract_abstract_europepmc(provide_params_extract_abstract_fixture: dict):
    """Test extracting abstract from EuropePMC PDFs."""
    actual = SpacyPDF(provide_params_extract_abstract_fixture["europepmc"].pdfs()).get_publications()[0].abstract.text
    assert actual == provide_params_extract_abstract_fixture["expected_abstract"]
    if Path(output_dir).exists():
        shutil.rmtree(output_dir)


def test_extract_id():
    """Test extracting publication ID from user-provided PDF."""
    actual = SpacyPDF([PDF("tests/test_pdfs/test_pdf.pdf")]).get_publications()[0].id
    expected = "test_pdf"
    assert str(actual) == expected
    if Path(output_dir).exists():
        shutil.rmtree(output_dir)


@pytest.fixture(
    params=[
        {
            "id": "PMC12416454",
            "figure_descriptions": [
                "Figure 1. Coordination-driven self-assembly of L into stellated "
                "helical octahedral Pd6 L 8 and cuboctahedral Pd12 L 16 SCCs and "
                "their transformation reactions: a) using [Pd(ACN)4](BF4)2, b) "
                "using Pd(NO3)2. The blue asterisk denotes chiral centres of the "
                "steroid skeleton.",
                "Figure 2. NMR characterisation of Pd6 L 8 "
                "and Pd12L16. a) 1 HNMRspectra of L , mixture of Pd6 L 8 and "
                "Pd12 L 16 ( RM1 ), Pd6 L 8 ( RM2 3:2 ), and Pd12 L 16 ( RM2 ) "
                "in [D6]-DMSO at 298.2 K and 700 MHz. 1 HDOSY NMR spectra of b) "
                "Pd12 L 16 ( RM2 ) and c) Pd6 L 8 ( RM2 3:2 ) ([D6]-DMSO, 303.2 "
                "K and 700 MHz).",
                "Figure 3. Computational models and cartoon "
                "representations. a) PdC24 L 4 building subunit, b) Pd6 L 8, c) "
                "Pd12 L 16, and d) nomenclatures used for the triangular panel.",
                "Figure 4. Structural analysis of supramolecular coordination "
                "complexes using CD spectroscopy. a) CD spectra of ligands and "
                "their coordination complexes in methanol at 25 °C. Interpretation"
                " of helical structures of b) Pd6 L 8 or Pd12 L 16, and c) Pd3( "
                "L d )6 , following the C24-C3-Pd-C3-C24 backbone.",
                "Figure 5. "
                "Toxicological studies of the SCCs. a) Concentration-response of "
                "HepG2 spheroid viability (ATP content) after 8 days of exposure "
                "to Pd(NO3)2, L , Pd6 L 8, and Pd12 L 16. The asterisk (*) "
                "indicates a statistically significant ( P < 0.05) "
                "di/uniFB00erence from the solvent control. b) Relation"
                " of spheroid viability to palladium content measured "
                "in spheroids. ρ represents Spearman's rank correlation"
                " coe/uniFB03cient with a P value.",
            ],
        },
    ],
)
def provide_params_extract_figure_descriptions(request: pytest.FixtureRequest):
    """Provide parameters for extract figure descriptions fixture."""
    europepmc = EuropePMC(request.param["id"])
    data = {
        "europepmc": europepmc,
        "figure_descriptions": request.param["figure_descriptions"],
    }
    yield data
    if Path(europepmc.storage).exists():
        shutil.rmtree(europepmc.storage)


def test_extract_figure_descriptions(provide_params_extract_figure_descriptions: dict):
    """Test extracting figure descriptions from EuropePMC PDFs."""
    actual = (
        SpacyPDF(provide_params_extract_figure_descriptions["europepmc"].pdfs())
        .get_publications()[0]
        .figure_descriptions
    )
    expected = provide_params_extract_figure_descriptions["figure_descriptions"]
    assert actual == expected
    if Path(output_dir).exists():
        shutil.rmtree(output_dir)


@pytest.fixture(
    params=[
        {
            "id": "PMC12663392",
            "table": pd.DataFrame(
                {
                    "Usage": [
                        "pRR-PGRN C126f",
                        "pRR-PGRN C126r",
                        "pRR PGRN W386f",
                        "pRR PGRN W386r",
                    ],
                    "Sequence": [
                        "TCGACTGCCATCCAGTGCCCTGATAGTCAGTTCGAATGCCCGA",
                        "CTAGTCGGGCATTCGAACTGACTATCAGGGCACTGGATGGCAG",
                        "TCGACCCTGCTGCCAACTCACGTCTGGGGAGTGGGGCA",
                        "CTAGTGCCCCACTCCCCAGACGTGAGTTGGCAGCAGGG",
                    ],
                },
            ),
        },
    ],
)
def provide_params_extract_tables(request: pytest.FixtureRequest):
    """Provide parameters for extract tables fixture."""
    europepmc = EuropePMC(request.param["id"])
    data = {
        "europepmc": europepmc,
        "table": request.param["table"],
    }
    yield data
    if Path(europepmc.storage).exists():
        shutil.rmtree(europepmc.storage)


def test_extract_tables(provide_params_extract_tables: dict):
    """Test extracting tables from EuropePMC PDFs."""
    actual = SpacyPDF(provide_params_extract_tables["europepmc"].pdfs()).get_publications()
    expected = provide_params_extract_tables["table"].reset_index(drop=True)
    number_of_tables = 5
    pd.testing.assert_frame_equal(actual[0].tables[2].reset_index(drop=True), expected, check_like=True)
    assert len(actual[0].tables) == number_of_tables
    if Path(output_dir).exists():
        shutil.rmtree(output_dir)
