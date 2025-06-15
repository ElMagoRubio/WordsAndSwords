import argparse
import os
from huggingface_hub import create_repo, upload_folder

# Configurar argumentos
parser = argparse.ArgumentParser(
    description="Sube un modelo local a Hugging Face Hub."
)

parser.add_argument(
    "--create_repo",
    action="store_true",
    help="Crea el repositorio en Hugging Face si no existe"
)

parser.add_argument(
    "model_path",
    type=str,
    help="Ruta local al directorio del modelo"
)

parser.add_argument(
    "model_name",
    type=str,
    help="Nombre del repositorio en Hugging Face (por ejemplo: SmolLM2-360M-Instruct-lora)"
)

parser.add_argument(
    "--commit_message",
    type=str,
    default="subida inicial",
    help="Mensaje de commit (por defecto: 'subida inicial')"
)

# Parsear argumentos
args = parser.parse_args()

# Construir ruta y ID del repositorio
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.abspath(os.path.join(BASE_DIR, args.model_path))
repo_id = f"ElMagoRubio/{args.model_name}"

# Validaciones básicas
if not os.path.isdir(folder_path):
    raise ValueError(f"La ruta del modelo no existe o no es un directorio: {folder_path}")

# Crear el repositorio si se solicita
if args.create_repo:
    print(f"[INFO] Creando repositorio {repo_id} en Hugging Face Hub...")
    create_repo(args.model_name, private=False, repo_type="model")

# Subir los archivos
print(f"[INFO] Subiendo carpeta: {folder_path}")
upload_folder(
    repo_id=repo_id,
    folder_path=folder_path,
    commit_message=args.commit_message
)

print(f"[ÉXITO] Modelo subido a https://huggingface.co/{repo_id}")
