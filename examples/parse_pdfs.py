import os
from pathlib import Path
import yaml
from aoptk.literature.pdf import PDF
from aoptk.literature.pymupdf_parser import PymupdfParser
from aoptk.text_generation_api import TextGenerationAPI

litellm_config_file = os.environ.get("LITELLM_CONFIG_FILE")

if litellm_config_file:
    with Path.open(litellm_config_file) as f:
        config = yaml.safe_load(f)
    litellm_api_key = os.environ.get("LITELLM_API_KEY")
    text_generation = TextGenerationAPI(model="qwen3.5", api_key=litellm_api_key)
else:
    text_generation = None

Path("parsed").mkdir()
pdfs = [PDF(pdf_path) for pdf_path in Path("pdfs").iterdir() if pdf_path.is_file()]
publications = PymupdfParser(pdfs, figure_storage="./figures", text_generation=text_generation).get_publications(
    download_figures_enabled=True,
)
for pub in publications:
    with Path.open(f"parsed/{pub.id}.txt", "w") as f:
        f.write(pub.full_text)
