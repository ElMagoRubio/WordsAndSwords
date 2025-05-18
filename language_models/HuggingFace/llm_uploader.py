from huggingface_hub import create_repo, upload_folder
import os

MODEL_NAME = "HuggingFaceTB_SmolLM2-360M-Instruct-finetuned_v1"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(BASE_DIR, f"../model/{MODEL_NAME}")

create_repo("SmolLM2-360M-Instruct-WnS-v1", private=False)
upload_folder(
    repo_id = "ElMagoRubio/SmolLM2-WnS",
    folder_path = F"../model/{MODEL_NAME}",
    commit_message = "subida inicial"
)