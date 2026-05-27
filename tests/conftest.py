from pathlib import Path
import pytest
from aoptk.literature.databases.pmc import PMC
from aoptk.literature.id import ID

# ruff: noqa: E501


@pytest.fixture(
    scope="package",
    params=[
        {
            "id": ID("PMC12416454"),
            "expected_abstract": Path("tests/test_data/PMC12416454_abstract.txt").read_text(encoding="utf-8"),
            "full_text": Path("tests/test_data/PMC12416454.txt").read_text(encoding="utf-8"),
            "figures": [
                "tests/figure_storage/PMC12416454/figure1.png",
                "tests/figure_storage/PMC12416454/figure2.png",
                "tests/figure_storage/PMC12416454/figure3.png",
                "tests/figure_storage/PMC12416454/figure4.png",
                "tests/figure_storage/PMC12416454/figure5.png",
            ],
            "figure_size": 3169271,
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
            "tables": 0,
        },
        {
            "id": ID("PMC12231352"),
            "expected_abstract": Path("tests/test_data/PMC12231352_abstract.txt").read_text(encoding="utf-8"),
            "full_text": Path("tests/test_data/PMC12231352.txt").read_text(encoding="utf-8"),
            "figures": [
                "tests/figure_storage/PMC12231352/figure1.png",
                "tests/figure_storage/PMC12231352/figure2.png",
                "tests/figure_storage/PMC12231352/figure3.png",
                "tests/figure_storage/PMC12231352/figure4.png",
                "tests/figure_storage/PMC12231352/figure5.png",
                "tests/figure_storage/PMC12231352/figure6.png",
                "tests/figure_storage/PMC12231352/figure7.png",
                "tests/figure_storage/PMC12231352/figure8.png",
                "tests/figure_storage/PMC12231352/figure9.png",
            ],
            "figure_size": 16224618,
            "figure_descriptions": [
                "FIGURE 1 The extraction and puriﬁcation of BSP-1.",
                "FIGURE 2 Brief steps of in vivo experiments, observation and recording of rat body weight, and pathological changes in liver tissue. (A) Grouping of experimental Animals. (B) The body weight of rats. (C) The hepatic index of rats. (D) The oil red area of liver tissue in rats. (E) The effect of BSP-1 on liver tissue in rats (anatomical observations and H&E stainning, Oil red stainning, 100 ×). The data are shown as the means ± SDs. #p < 0.05, ##p < 0.01, ###p < 0.001, vs. the control group; *p < 0.05, **p < 0.01, ***p < 0.001, vs. the model group.",
                "FIGURE 3 Brief steps in vitro experiments, cytotoxicity test of BSP-1, detection of liver function and TC, TG levels, and Oil red staining in HepG2 cells. (A) CCK8 assay in HepG2 cells. (B) HepG2 cells and culture. (C) CCK8 assay in HepG2 cells. The measurement of (D) ALT (E) AST (F) TC (G) TG in HepG2 cells. (H) The oil red area of liver tissue in HepG2 cells. (I) The effect of BSP-1 in HepG2 cells (Oil red stainning, 100 ×). The data are shown as the means ± SDs. #p < 0.05, ##p < 0.01, ###p < 0.001, vs. the control group; *p < 0.05, **p < 0.01, ***p < 0.001, vs. the model group.",
                "FIGURE 4 Characterization of BSP. (A) The UV Spectroscopy of BSP-1. (B) The average molecular weight of BSP-1. (C) The monosaccharide composition of BSP-1.",
                "FIGURE 5 Measurement of IL-1β, IL-18, TC, TG, liver function in rat serum and qRT-PCR analysis in rat liver tissue. The measurement of (A) IL-1β (B) IL- 18 (C) ALT (D) AST (E) TC (F) TG in rat serum. The mRNA levels of (G) the NLRP3 (H) the ASC (I) the caspase-1 (J) the GSDMD in rat liver tissue. The data are shown as the means ± SDs. #p < 0.05, ##p < 0.01, ###p < 0.001, vs. the control group; *p < 0.05, **p < 0.01, ***p < 0.001, vs. the model group.",
                "FIGURE 6 Measurement of IL-1β and IL-18, qRT-PCR and WB analysis in HepG2 cells. The measurement of (A) IL-1β and (B) IL-18 in HepG2 cells. The mRNA levels of (C) the NLRP3 (D) the ASC (E) the caspase-1 and (F) the GSDMD in HepG2 cells. (G) The WB analysis in HepG2 cells. (H) The NLRP3/β-Actin (I) the ASC/β-Actinof (J) the Cleaved-caspase-1/β-Actin and (K) the Cleaved-GSDMD/β-Actinof WB in HepG2 cells. The data are shown as the means ± SDs. #p < 0.05, ##p < 0.01, ###p < 0.001, vs. the control group; *p < 0.05, **p < 0.01, ***p < 0.001, vs. the model group.",
                "FIGURE 7 The WB analysis and immunohistochemical staining in rat liver tissue. (A) The WB analysis in rat liver tissue. (B) The NLRP3/β-Actin (C) the ASC/β- Actinof (D) the Cleaved-caspase-1/β-Actin and (E) the Cleaved-GSDMD/β-Actinof WB in rat liver tissue. (F) The evaluation of NLRP3 and GSDMD immunohistochemical staining (200 ×). The immunohistochemical density of (G) the NLRP3 and (H) the GSDMD in rat liver tissue. The data are shown as the means ± SDs. #p < 0.05, ##p < 0.01, ###p < 0.001, vs. the control group; *p < 0.05, **p < 0.01, ***p < 0.001, vs. the model group.",
                "FIGURE 8 Immunoﬂuorescence of HepG2 Cells. (A) The evaluation of NLRP3 immunoﬂuorescence staining (100 ×). The immunohistochemical density of (B) the NLRP3 and (C) the GSDMD in HepG2 cells. (D) The evaluation of GSDMD immunoﬂuorescence staining (100 ×). The data are shown as the means ± SDs. #p < 0.05, ##p < 0.01, ###p < 0.001, vs. the control group; *p < 0.05, **p < 0.01, ***p < 0.001, vs. the model group.",
                "FIGURE 9 The impact of BSP-1 on MASLD by evaluating its ability to reduce the expression of pyroptosis-related NLRP3/caspase-1/GSDMD pathway in both HFD-induced rat models in vivo and FFA-induced HepG2 cells in vitro.",
            ],
            "tables": 1,
        },
        {
            "id": ID("PMC12181427"),
            "expected_abstract": Path("tests/test_data/PMC12181427_abstract.txt").read_text(encoding="utf-8"),
            "full_text": Path("tests/test_data/PMC12181427.txt").read_text(encoding="utf-8"),
            "figures": [
                "tests/figure_storage/PMC12181427/figure1.png",
                "tests/figure_storage/PMC12181427/figure10.png",
                "tests/figure_storage/PMC12181427/figure11.png",
                "tests/figure_storage/PMC12181427/figure12.png",
                "tests/figure_storage/PMC12181427/figure2.png",
                "tests/figure_storage/PMC12181427/figure3.png",
                "tests/figure_storage/PMC12181427/figure4.png",
                "tests/figure_storage/PMC12181427/figure5.png",
                "tests/figure_storage/PMC12181427/figure6.png",
                "tests/figure_storage/PMC12181427/figure7.png",
                "tests/figure_storage/PMC12181427/figure8.png",
                "tests/figure_storage/PMC12181427/figure9.png",
            ],
            "figure_size": 15219930,
            "figure_descriptions": [
                "Fig. 1 .  Scan electron microscope images for samples 3a-c , 5a-c (1000× magnification) showing surface morphology of thin films prepared via spin coating.",
                "Fig. 2 .  Surface plot and surface roughness curves for samples 3a-c and 5a-c .",
                "Fig. 3 .  Korsmeyer-Peppas drug release model for samples 3a-c , 5a-c : excellent fit with R 2 values ranging from 0.99 to 1, indicating high correlation between experimental and theoretical data.",
                "Fig. 4 .  Displays optical micrographs captured using an inverted microscope, showing HepG-2 cancer cells on various substrates: ( a ) 3a-c and 5a-c , rounded, detached cells are often indicative of dying cells, while those maintaining the typical elongated shape are likely still alive, control cells: ( b ) morphology and distribution of HepG-2 cells without substrate intervention.",
                "Fig. 5 .  Boxplot comparison of cell area across the control and treated groups. Cell area (µm 2 ), vs. experimental groups. The control group shows the highest variability and extreme outliers, while all treated groups exhibit reduced spread and fewer outliers, indicating more uniform cell sizes post-treatment.",
                "Fig. 6 .  Swiss target prediction scanning for compounds 3a-c , 5a-c .",
                "Fig. 7 .  The interaction between 3-methylthiophene 5b and (PDB ID: 4e4l).",
                "Fig. 8 .  ( a ) Optimized structures, ( b ) electron density, ( c ) HOMO and LUMO for compound 5b .",
            ],
            "tables": 3,
        },
    ],
    ids=["PMC12416454", "PMC12231352", "PMC12181427"],
)
def provide_publications(request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory):
    """Provide parameters for publication fixture, including PDFs."""
    pmc = PMC(
        storage=tmp_path_factory.mktemp(f"{request.param['id']}"),
        figure_storage=tmp_path_factory.mktemp(f"{request.param['id']}_figures"),
    )
    request.param.update(
        {
            "pdfs": pmc.get_pdfs(ids=[request.param["id"]]),
        },
    )
    return request.param


@pytest.fixture(scope="module")
def provide_temp_storage(provide_publications: dict, tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Provide temporary directories for storage of full text and figures."""
    pub_id = provide_publications["id"]
    return tmp_path_factory.mktemp(f"{pub_id}")


@pytest.fixture(scope="module")
def provide_temp_storage_figures(provide_publications: dict, tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Provide temporary directories for storage of full text and figures."""
    pub_id = provide_publications["id"]
    return tmp_path_factory.mktemp(f"{pub_id}_figures")
