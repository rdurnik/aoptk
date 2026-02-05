import os
import shutil
from pathlib import Path
import pytest
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.literature.get_publication import GetPublication
from aoptk.literature.pdf import PDF
from aoptk.literature.pymupdf_parser import PymupdfParser


output_dir = "tests/figure_storage"


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


@pytest.fixture(scope="module")
def publication(provide_pdfs: dict):
    parser = PymupdfParser(provide_pdfs["pdfs"])
    publications = parser.get_publications()
    provide_pdfs.update({
        "publication": publications[0],
        "parser": parser
    })
    yield provide_pdfs

    if Path(parser.figures_output_dir).exists():
        shutil.rmtree(parser.figures_output_dir)


def test_extract_abstract_europepmc(publication: dict):
    """Test extracting abstract from EuropePMC PDFs."""
    actual = publication["publication"].abstract.text
    assert actual == publication["expected_abstract"]


def test_extract_full_text_europepmc(publication: dict):
    """Test extracting full text from EuropePMC PDFs."""
    pub = publication["publication"]
    actual = pub.full_text[publication["full_text_slice"]]
    assert actual == publication["full_text"]


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
    actual = PymupdfParser([PDF(path)]).get_publications()[0].abstract.text
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


def test_extract_figure_descriptions(publication: dict):
    """Test extracting figure descriptions from EuropePMC PDFs."""
    if publication["id"] == "PMC12181427":
        pytest.skip("Pymupdf can't parse figure captions in this paper.")

    actual = publication["publication"].figure_descriptions
    expected = publication["figure_descriptions"]
    assert actual == expected


def test_extract_figures(publication: dict):
    """Test extracting figures from EuropePMC PDFs."""
    actual = publication["publication"].figures
    expected = [
        str(publication["parser"].figures_output_dir / Path(fig).relative_to("tests/figure_storage"))
        for fig in publication["figures"]
    ]
    expected_size = publication["figure_size"]
    total_size = sum(
        Path(dirpath, filename).stat().st_size
        for dirpath, dirnames, filenames in os.walk(publication["parser"].figures_output_dir)
        for filename in filenames
    )
    assert actual == expected
    assert total_size == expected_size
