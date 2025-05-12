from huggingface_hub import login
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    AutoModelForCausalLM, 
    AutoModelForSeq2SeqLM
)
import os


# Obtener la ruta absoluta del directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_list = [
    ("lxyuan/distilbert-base-multilingual-cased-sentiments-student", AutoModelForSequenceClassification), 
    ("HuggingFaceTB/SmolLM2-360M-Instruct", AutoModelForCausalLM),
    ("google/flan-t5-large", AutoModelForSeq2SeqLM)
]

for model_name, ModelClass in model_list:
    print(f"Descargando y guardando el modelo: {model_name}")

    #Reemplazando "/" por "_" para evitar problemas con los nombres de los archivos
    safe_model_name = model_name.replace("/", "_")

    #Descarga y guardado del tokenizador
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.save_pretrained(os.path.join(BASE_DIR,"tokenizer", safe_model_name))
    
    #Descarga y guardado del modelo con su tipo específico
    model = ModelClass.from_pretrained(model_name)
    model.save_pretrained(os.path.join(BASE_DIR, "model/", safe_model_name))

    print(f"Modelo {model_name} guardado en './model/{safe_model_name}' y su tokenizador en './tokenizer/{safe_model_name}'\n")