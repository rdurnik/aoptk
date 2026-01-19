from __future__ import annotations
import os
import pytest
import shutil
from pathlib import Path
from aoptk.spacy_pdf_processor import SpacyPDF
from aoptk.literature.get_publication import GetPublication
from aoptk.literature.pdf import PDF
from aoptk.literature.databases.europepmc import EuropePMC

output_dir = "/home/rdurnik/aoptk/tests/figure_storage"

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


pytestmark = pytest.mark.skipif(
    IN_GITHUB_ACTIONS,
    reason="Skip in Github Actions to save energy consumption (large model download required).",
)


def test_can_create():
    """Can create SpacyPDF instance."""
    actual = SpacyPDF([])
    assert actual is not None


def test_implements_interface_get_publication():
    """SpacyPDF implements GetPublication interface."""
    assert issubclass(SpacyPDF, GetPublication)


def test_get_publications_not_empty():
    """Test that get_publications method returns a non-empty result."""
    actual = SpacyPDF([PDF('tests/test_pdfs/test_pdf.pdf')]).get_publications()
    assert actual is not None

@pytest.fixture(
    params=[
        {"id": "PMC12416454", "paragraph_number": 3, "full_text": "Natural chiral hydrophobic cavities are important for many biological functions, e.g., for recognition as parts of transport proteins or for substrate-specific transformations as parts of enzymes. To understand and mimic these natural systems and their (supra)molecular mechanisms of action, the development of their artificial counterparts (e.g., cages, macrocycles) from chiral molecules is desirable. Easing such efforts, nature readily offers convenient chiral building blocks (terpenoids, amino acids, or carbohydrates) which can be utilized. Intermolecular-interaction-mediated self-assembly together with metal coordination are essential natural processes to construct such higher-order structures and can easily be adapted in the development of artificial systems."},
        {
            "id": "PMC12638863",
            "paragraph_number": 5,
            "full_text": "In  our  previous  paper  we  shed  light  on  the  impact  of  cellular  respiration  altering  the  mitochondrial temperature  in  both  health  and  disease 35 .  Moreover,  recent  studies  reported  that  Warburg  effect  in  HCC affect the mitochondrial temperature 38,39 .  Hernin, we investigated the impact of this metabolic switch on the mitochondrial temperature in HCC. Cancer cells were treated with metformin to suppress glycolysis to emulate lower metabolically active cancer cells.",
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