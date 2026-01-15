from aoptk.literature.pymupdf_parser import PymupdfParser
from aoptk.literature.pdf import PDF

abstract = PymupdfParser([PDF("src/aoptk/1-s2.0-S0013935120315784-main.pdf")]).get_publications()[0].abstract
full_text = PymupdfParser([PDF("src/aoptk/1-s2.0-S0013935120315784-main.pdf")]).get_publications()[0].full_text

# "Exposure to environmental chemicals, particularly those with persistent and bioaccumulative properties have been linked to liver diseases. Induction of fibrotic pathways is considered as a pre-requirement of chemical induced liver fibrosis. Here, we applied 3D in vitro human liver microtissues (MTs) composed of HepaRG, THP-1 and hTERT-HSC that express relevant hepatic pathways (bile acid, sterol, and xenobiotic metabolism) and can recapitulate key events of liver fibrosis (e.g. extracellular matrix-deposition). The liver MTs were exposed to a known profibrotic chemical, thioacetamide (TAA) and three representative environmental chemicals (TCDD, benzo [a] pyrene (BaP) and PCB126). Both TAA and BaP triggered fibrotic pathway related events such as hepatocellular damage (cytotoxicity and decreased albumin release), hepatic stellate cell activation (transcriptional upregulation of α-SMA and Col1α1) and extracellular matrix remodelling. TCDD or PCB126 at measured concentrations did not elicit these responses in the 3D liver MTs system, though they caused cytotoxicity in HepaRG monoculture at high concentrations. Reduced human transcriptome (RHT) analysis captured molecular responses involved in liver fibrosis when MTs were treated with TAA and BaP. The results suggest that 3D, multicellular, human liver microtissues represent an alternative, human-relevant, in vitro liver model for assessing fibrotic pathways induced by environmental chemicals."

text_translated = TextGenerationAPI().translate_abbreviation(text=abstract)
print(text_translated)

chemicals = TextGenerationAPI().find_chemical(text=text_translated)
print(chemicals)
for chemical in chemicals:
    print(f"Chemical found: {chemical.name}")

relationships = TextGenerationAPI().find_relationships(
    text=text_translated, chemicals=chemicals, effects=[Effect(name="stellate cell activation"), Effect(name="cytotoxicity")],
)
print(relationships)
for relationship in relationships:
    print(
        f"Relationship found: {relationship.chemical.name} - {relationship.relationship} - {relationship.effect.name}",
    )
