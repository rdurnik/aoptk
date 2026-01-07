import os
import shutil
from pathlib import Path
import pytest
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.literature.get_publication import GetPublication
from aoptk.literature.id import ID
from aoptk.literature.pdf import PDF
from aoptk.literature.pymupdf_parser import PymupdfParser

output_dir = "/home/rdurnik/aoptk/tests/figure_storage"


def test_can_create():
    """Test that PymupdfParser can be instantiated."""
    actual = PymupdfParser(str)
    assert actual is not None


def test_implements_interface():
    """Test that PymupdfParser implements GetPublication interface."""
    assert issubclass(PymupdfParser, GetPublication)


def test_get_publication_data_not_empty():
    """Test that get_publications method returns non-empty list."""
    actual = PymupdfParser("").get_publications()
    assert actual is not None


@pytest.fixture(
    params=[
        {
            "id": ID("PMC12416454"),
            "expected_abstract": "The rational design and "
            "selective self-assembly of ﬂexible and unsymmetric"
            " ligands into large coordination complexes is an"
            " eminent challenge in supramolecular coordination"
            " chemistry. Here, we present the coordination-driven"
            " self-assembly of natural ursodeoxycholic-bile-acid-derived"
            " unsymmetric tris-pyridyl ligand (L) resulting in "
            "the selective and switchable formation of chiral "
            "stellated Pd6L8 and Pd12L16 cages. The selectivity "
            "of the cage originates in the adaptivity and ﬂexibility "
            "of the arms of the ligand bearing pyridyl moieties. The "
            "interspeciﬁc transformations can be controlled by changes"
            " in the reaction conditions. The orientational self-sorting "
            "of L into a single constitutional isomer of each cage,"
            " i.e., homochiral quadruple and octuple right-handed "
            "helical species, was conﬁrmed by a combination of"
            " molecular modelling and circular dichroism. The "
            "cages, derived from natural amphiphilic transport "
            "molecules, mediate the higher cellular uptake and "
            "increase the anticancer activity of bioactive "
            "palladium cations as determined in studies using "
            "in vitro 3D spheroids of the human hepatic cells HepG2.",
        },
        {
            "id": ID("PMC12231352"),
            "expected_abstract": "1School of Clinical Medical, Hubei University of Chinese Medicine, "
            "Wuhan, China, 2Department of Gastroenterology, Hubei Provincial Hospital "
            "of Integrated Chinese and Western Medicine, Wuhan, China, 3Department of "
            "Health Management Center, Hubei Provincial Hospital of Traditional Chinese "
            "Medicine, Wuhan, China\n"
            "Background: The role of nucleotide-binding oligomerization domain-like "
            "receptors containing pyrin domain 3 (NLRP3) inﬂammasome and pyroptosis in "
            "the inﬂammatory microenvironment of metabolic-associated fatty liver disease"
            " (MASLD) has been posited as crucial. Bletilla striata polysaccharides (BSPs),"
            " extracted from the tubers of Bletilla striata (Thunb.) Rchb.f., exhibit signiﬁcant"
            " anti-inﬂammatory properties. However, their potential protective effects "
            "on MASLD and their role in regulating pyroptosis remain unclear.\n"
            "Objectives: This study investigates the efﬁcacy of BSP-1, a puriﬁed "
            "metabolite isolated from crude BSPs, on MASLD by evaluating its ability"
            " to modulate the NLRP3/caspase-1/GSDMD signaling pathway.\n"
            "Methods: To simulate MASLD in vivo and in vitro, high-fat diet (HFD)-induced"
            " rat models and free fatty acid (FFA)-stimulated HepG2 cells were used. "
            "Serum indicators and histopathological staining were employed to assess "
            "liver injury and lipid deposition. Additionally, enzyme-linked immunosorbent "
            "assay (ELISA), immunohistochemistry (IHC), immunoﬂuorescence, real-time quantitative"
            " polymerase chain reaction (RT-qPCR), and western blotting (WB) analysis"
            " were conducted to examine the NLRP3/caspase-1/GSDMD pathway and related cytokine levels.\n"
            "Results: BSP-1 signiﬁcantly ameliorates alanine aminotransferase (ALT), "
            "aspartate aminotransferase (AST), total cholesterol (TC), and triglyceride "
            "(TG) levels in both rat serum and HepG2 cells. Furthermore, BSP-1 reduces "
            "inﬂammatory factors interleukin (IL)-1β and IL-18, while improving pathological "
            "changes in rat liver tissue. Mechanistically, BSP-1 regulates the expression of"
            " pyroptosis-related proteins and mRNAs in the NLRP3/caspase-1/GSDMD pathway, "
            "thereby protecting against MASLD.\n"
            "Discussion: BSP-1 may represent a promising therapeutic agent for MASLD treatment"
            " by inhibiting the NLRP3/caspase-1/GSDMD signaling pathway.",
        },
        {
            "id": ID("PMC12181427"),
            "expected_abstract": "This study explores the potential of six novel "
            "thiophene derivative thin films (THIOs) for reducing cancer cell adhesion"
            " and enhancing controlled drug release on inert glass substrates. Thiophene"
            " derivatives 3a–c and 5a–c were synthesized and characterized using IR, 1H NMR,"
            " 13C NMR, and elemental analysis before being spin-coated onto glass to form thin"
            " films. SEM analysis and roughness measurements were used to assess their "
            "structural and functional properties. Biological evaluations demonstrated "
            "that the films significantly reduced HepG2 liver cancer cell adhesion "
            "(~ 78% decrease vs. control) and enabled controlled drug release, "
            "validated through the Korsmeyer-Peppas model (R2 > 0.99). Theoretical"
            " studies, including in-silico target prediction, molecular docking with"
            " JAK1 (PDB: 4E4L), and DFT calculations, provided insights into the "
            "electronic properties and chemical reactivity of these compounds. Notably,"
            " compound 5b exhibited the best binding energy (-7.59 kcal/mol) within the"
            " JAK1 pocket, aligning with its observed apoptotic behavior in cell culture."
            " DFT calculations further revealed that 5b had the lowest calculated energy"
            " values; -4.89 eV (HOMO) and − 3.22 eV (LUMO), and the energy gap was found to"
            " be 1.66 eV, supporting its role in JAK1 inhibition and cancer cell adhesion"
            " reduction. These findings underscore the promise of thiophene derivatives"
            " in biomedical applications, potentially leading to safer surgical "
            "procedures and more effective localized drug delivery systems.",
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
    actual = PymupdfParser(provide_params_extract_abstract_fixture["europepmc"].pdfs()).get_publications()[0].abstract
    assert actual == provide_params_extract_abstract_fixture["expected_abstract"]
    if Path(output_dir).exists():
        shutil.rmtree(output_dir)


@pytest.fixture(
    params=[
        {"id": "PMC12416454", "full_text_slice": slice(13, 39), "full_text": "Natural chiral hydrophobic"},
        {
            "id": "PMC12231352",
            "full_text_slice": slice(1444, 1484),
            "full_text": "Metabolic-associated fatty liver disease",
        },
        {"id": "PMC12181427", "full_text_slice": slice(108, 127), "full_text": "Surgical tools used"},
    ],
)
def provide_params_extract_full_text_fixture(request: pytest.FixtureRequest):
    """Provide parameters for extract full text fixture."""
    europepmc = EuropePMC(request.param["id"])
    data = {
        "europepmc": europepmc,
        "full_text_slice": request.param["full_text_slice"],
        "full_text": request.param["full_text"],
    }
    yield data
    if Path(europepmc.storage).exists():
        shutil.rmtree(europepmc.storage)


def test_extract_full_text_europepmc(provide_params_extract_full_text_fixture: dict):
    """Test extracting full text from EuropePMC PDFs."""
    actual = (
        PymupdfParser(provide_params_extract_full_text_fixture["europepmc"].pdfs())
        .get_publications()[0]
        .full_text[provide_params_extract_full_text_fixture["full_text_slice"]]
    )
    assert actual == provide_params_extract_full_text_fixture["full_text"]
    if Path(output_dir).exists():
        shutil.rmtree(output_dir)


@pytest.mark.parametrize(
    ("path", "expected_abstract"),
    [
        (
            "tests/test_pdfs/test_pdf.pdf",
            "Thioacetamide (TAA) is a widely utilized model "
            "hepatotoxicant, yet its cellular impact in advanced"
            " three-dimensional liver-mimetic systems continues "
            "to be characterized. HepG2 spheroids—derived from hepatocellular"
            " carcinoma cells cultured under conditions that promote "
            "multicellular aggregation— offer improved physiological "
            "relevance compared with conventional 2D monolayers due to "
            "enhanced cell–cell communication, more representative metabolic"
            " profiles, and the formation of nutrient and oxygen gradients "
            "that approximate aspects of in vivo liver tissue. In this study "
            "context, the responses of HepG2 spheroids to TAA exposure were "
            "examined to better understand how three-dimensional architecture"
            " influences toxicant susceptibility and downstream stress "
            "signaling. The spheroids exhibited a spectrum of reactions "
            "consistent with hepatocellular injury, including metabolic "
            "perturbation, oxidative imbalance, and modulation of survival"
            " and stress pathways. These responses appeared to emerge not "
            "only from direct chemical insult but also from the layered "
            "microenvironment inherent to spheroid organization, which "
            "shapes diffusion dynamics and cellular heterogeneity. "
            "Collectively, these observations underscore the usefulness "
            "of HepG2 spheroids as an intermediate-complexity system for "
            "modeling hepatotoxicity, enabling the capture of multicellular "
            "stress patterns that are often attenuated or absent in 2D "
            "cultures. The findings support the growing interest in 3D "
            "liver models as more predictive platforms for mechanistic "
            "toxicology and preclinical safety assessment.",
        ),
    ],
)
def test_extract_abstract_self_made_pdf(path: str, expected_abstract: str):
    """Test extracting abstract from self-made PDF."""
    actual = PymupdfParser([PDF(path)]).get_publications()[0].abstract
    assert actual == expected_abstract
    if Path(output_dir).exists():
        shutil.rmtree(output_dir)


@pytest.mark.parametrize(
    ("path", "where", "expected"),
    [
        ("tests/test_pdfs/test_pdf.pdf", slice(0, 29), "Thioacetamide (TAA) is widely"),
    ],
)
def test_extract_full_text_self_made_pdf(path: str, where: slice, expected: str):
    """Test extracting full text from self-made PDF."""
    actual = PymupdfParser([PDF(path)]).get_publications()[0].full_text[where]
    assert actual == expected
    if Path(output_dir).exists():
        shutil.rmtree(output_dir)


@pytest.fixture(
    params=[
        {
            "id": "PMC12637301",
            "abbreviation_list": [
                ("A3SS", "alternative 3′ splice site"),
                ("A5SS", "alternative 5′ splice site"),
                ("WB", "Western Blot"),
            ],
        },
        {"id": "PMC12231352", "abbreviation_list": []},
        {
            "id": "PMC11339729",
            "abbreviation_list": [
                ("BEB", "binary-encounter-Bethe"),
                ("CID", "collision-induced dissociation"),
                ("UFF", "universal force field"),
            ],
        },
        {
            "id": "PMC9103499",
            "abbreviation_list": [("ABC", "ATP-binding cassette"), ("AQP", "Aquaporin"), ("VDR", "Vitamin D receptor")],
        },
        {
            "id": "PMC12577378",
            "abbreviation_list": [
                ("AD-MSCs", "Adipose mesenchymal stem cells"),
                ("AKT", "Protein kinase B"),
                ("VEGF", "Vascular endothelial growth factor"),
            ],
        },
    ],
)
def provide_params_extract_abbreviations_fixture(request: pytest.FixtureRequest):
    """Provide parameters for extract abbreviations fixture."""
    europepmc = EuropePMC(request.param["id"])
    data = {
        "europepmc": europepmc,
        "abbreviation_list": request.param["abbreviation_list"],
    }
    yield data
    if Path(europepmc.storage).exists():
        shutil.rmtree(europepmc.storage)


def test_extract_abbreviations(provide_params_extract_abbreviations_fixture: dict):
    """Test extracting abbreviations from EuropePMC PDFs."""
    abbrev_dict = (
        PymupdfParser(provide_params_extract_abbreviations_fixture["europepmc"].pdfs())
        .get_publications()[0]
        .abbreviations
    )
    expected_list = provide_params_extract_abbreviations_fixture["abbreviation_list"]

    if expected_list:
        actual = [next(iter(abbrev_dict.items())), list(abbrev_dict.items())[1], list(abbrev_dict.items())[-1]]
        assert actual == expected_list
    else:
        assert abbrev_dict == {}
    if Path(output_dir).exists():
        shutil.rmtree(output_dir)


def test_extract_id():
    """Test extracting publication ID from user-provided PDF."""
    actual = PymupdfParser([PDF("tests/test_pdfs/test_pdf.pdf")]).get_publications()[0].id
    expected = "test_pdf"
    assert str(actual) == expected
    if Path(output_dir).exists():
        shutil.rmtree(output_dir)


@pytest.fixture(
    params=[
        {
            "id": "PMC12416454",
            "figure_descriptions": [
                "Figure 1. Coordination-driven self-assembly of L into "
                "stellated helical octahedral Pd6L8 and cuboctahedral "
                "Pd12L16 SCCs and their transformation reactions: a) using"
                " [Pd(ACN)4](BF4)2, b) using Pd(NO3)2. The blue asterisk"
                " denotes chiral centres of the steroid skeleton.",
                "Figure 2. NMR characterisation of Pd6L8 and Pd12L16. a) "
                "1H NMR spectra of L, mixture of Pd6L8 and Pd12L16 (RM1), "
                "Pd6L8 (RM2 3:2), and Pd12L16 (RM2) in [D6]-DMSO at 298.2 K"
                " and 700 MHz. 1H DOSY NMR spectra of b) Pd12L16 (RM2) and "
                "c) Pd6L8 (RM2 3:2) ([D6]-DMSO, 303.2 K and 700 MHz).",
                "Figure 3. Computational models and cartoon representations. "
                "a) PdC24L4 building subunit, b) Pd6L8, c) Pd12L16, and d)"
                " nomenclatures used for the triangular panel.",
                "Figure 4. Structural analysis of supramolecular coordination"
                " complexes using CD spectroscopy. a) CD spectra of ligands and"
                " their coordination complexes in methanol at 25 °C. "
                "Interpretation of helical structures of b) Pd6L8 or "
                "Pd12L16, and c) Pd3(Ld)6, following the C24-C3-Pd-C3-C24 backbone.",
                "Figure 5. Toxicological studies of the SCCs. a) "
                "Concentration-response of HepG2 spheroid viability "
                "(ATP content) after 8 days of exposure to Pd(NO3)2, "
                "L, Pd6L8, and Pd12L16. The asterisk (*) indicates a "
                "statistically signiﬁcant (P < 0.05) diﬀerence from the "
                "solvent control. b) Relation of spheroid viability to "
                "palladium content measured in spheroids. ρ represents "
                "Spearman’s rank correlation coeﬃcient with a P value.",
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
        PymupdfParser(provide_params_extract_figure_descriptions["europepmc"].pdfs())
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
            "id": "PMC12416454",
            "figures": [
                "tests/figure_storage/PMC12416454/figure1.jpeg",
                "tests/figure_storage/PMC12416454/figure2.png",
                "tests/figure_storage/PMC12416454/figure3.png",
                "tests/figure_storage/PMC12416454/figure4.png",
                "tests/figure_storage/PMC12416454/figure5.png",
            ],
        },
    ],
)
def provide_params_extract_figures(request: pytest.FixtureRequest):
    """Provide parameters for extract figures fixture."""
    europepmc = EuropePMC(request.param["id"])
    data = {
        "europepmc": europepmc,
        "figures": request.param["figures"],
    }
    yield data
    if Path(europepmc.storage).exists():
        shutil.rmtree(europepmc.storage)


def test_extract_figures(provide_params_extract_figures: dict, tmp_path: Path):
    """Test extracting figures from EuropePMC PDFs."""
    figures_output_dir = str(tmp_path / "figure_storage")
    actual = (
        PymupdfParser(provide_params_extract_figures["europepmc"].pdfs(), figures_output_dir=figures_output_dir)
        .get_publications()[0]
        .figures
    )
    expected = [
        str(tmp_path / "figure_storage" / Path(fig).relative_to("tests/figure_storage"))
        for fig in provide_params_extract_figures["figures"]
    ]
    expected_size = 2493663
    total_size = sum(
        Path(dirpath, filename).stat().st_size
        for dirpath, dirnames, filenames in os.walk(figures_output_dir)
        for filename in filenames
    )
    assert actual == expected
    assert total_size == expected_size
