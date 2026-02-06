import shutil
from pathlib import Path
import pytest
from aoptk.literature.databases.europepmc import EuropePMC
from aoptk.literature.id import ID

# ruff: noqa: E501


@pytest.fixture(
    scope="package",
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
            "full_text_slice": slice(13, 39),
            "full_text": "Natural chiral hydrophobic",
            "figures": [
                "tests/figure_storage/PMC12416454/figure1.jpeg",
                "tests/figure_storage/PMC12416454/figure2.png",
                "tests/figure_storage/PMC12416454/figure3.png",
                "tests/figure_storage/PMC12416454/figure4.png",
                "tests/figure_storage/PMC12416454/figure5.png",
            ],
            "figure_size": 2493663,
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
            "paragraph_number": 15,
            "paragraph": "More than three decades after the first discovery, "
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
            "tables": 0,
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
            "full_text_slice": slice(1444, 1484),
            "full_text": "Metabolic-associated fatty liver disease",
            "figures": [
                "tests/figure_storage/PMC12231352/figure1.jpeg",
                "tests/figure_storage/PMC12231352/figure2.jpeg",
                "tests/figure_storage/PMC12231352/figure3.jpeg",
                "tests/figure_storage/PMC12231352/figure4.jpeg",
                "tests/figure_storage/PMC12231352/figure5.jpeg",
                "tests/figure_storage/PMC12231352/figure6.jpeg",
                "tests/figure_storage/PMC12231352/figure7.jpeg",
                "tests/figure_storage/PMC12231352/figure8.jpeg",
                "tests/figure_storage/PMC12231352/figure9.jpeg",
            ],
            "figure_size": 6167990,
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
            "paragraph_number": 5,
            "paragraph": "Methods: To simulate MASLD in vivo and in vitro , high-fat diet (HFD)-induced rat models and free fatty acid (FFA)-stimulated HepG2 cells were used. Serum indicators and histopathological staining were employed to assess liver injury and lipid deposition. Additionally, enzyme-linked immunosorbent assay (ELISA), immunohistochemistry (IHC), immuno /uniFB02 uorescence, real-time quantitative polymerase chain reaction (RT-qPCR), and western blotting (WB) analysis were conducted to examine the NLRP3/caspase-1/GSDMD pathway and related cytokine levels.",
            "tables": 1,
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
            "full_text_slice": slice(108, 127),
            "full_text": "Surgical tools used",
            "figures": [
                "tests/figure_storage/PMC12181427/figure1.png",
                "tests/figure_storage/PMC12181427/figure10.png",
                "tests/figure_storage/PMC12181427/figure11.jpeg",
                "tests/figure_storage/PMC12181427/figure12.jpeg",
                "tests/figure_storage/PMC12181427/figure2.jpeg",
                "tests/figure_storage/PMC12181427/figure3.png",
                "tests/figure_storage/PMC12181427/figure4.png",
                "tests/figure_storage/PMC12181427/figure5.png",
                "tests/figure_storage/PMC12181427/figure6.jpeg",
                "tests/figure_storage/PMC12181427/figure7.jpeg",
                "tests/figure_storage/PMC12181427/figure8.png",
                "tests/figure_storage/PMC12181427/figure9.png",
            ],
            "figure_size": 6852393,
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
            "paragraph_number": 7,
            "paragraph": "1 Department of Chemistry, Faculty of Science, Mansoura University, Mansoura 35516, Egypt.  2 Center of Excellence for Genome and Cancer Research, Urology and Nephrology Center, Mansoura University, El Dakhlia, Egypt. \uf02a email: hebama@mans.edu.eg; raghdaabogabal@gmail.com",
            "tables": 4,
        },
    ],
    ids=["PMC12416454", "PMC12231352", "PMC12181427"],
)
def provide_pdfs(request: pytest.FixtureRequest):
    """Provide parameters for extract abstract fixture."""
    europepmc = EuropePMC(request.param["id"])
    request.param.update(
        {
            "pdfs": europepmc.pdfs(),
        },
    )
    yield request.param
    if Path(europepmc.storage).exists():
        shutil.rmtree(europepmc.storage)
