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

# Lista de modelos con su clase y modelo base para el tokenizador
model_list = [
    # (modelo a descargar, clase de modelo, modelo base para tokenizer)
    ("lxyuan/distilbert-base-multilingual-cased-sentiments-student", AutoModelForSequenceClassification, "lxyuan/distilbert-base-multilingual-cased-sentiments-student"), 
    ("tabularisai/multilingual-sentiment-analysis", AutoModelForSequenceClassification, "tabularisai/multilingual-sentiment-analysis"),
    ("HuggingFaceTB/SmolLM2-360M-Instruct", AutoModelForCausalLM, "HuggingFaceTB/SmolLM2-360M-Instruct"),
    ("ElMagoRubio/SmolLM2-360M-Instruct-lora", AutoModelForCausalLM, "HuggingFaceTB/SmolLM2-360M-Instruct"),
    ("google/flan-t5-large", AutoModelForSeq2SeqLM, "google/flan-t5-large"),
    ("ElMagoRubio/flan-t5-large-lora", AutoModelForSeq2SeqLM, "google/flan-t5-large"),
    ("microsoft/Phi-4-mini-instruct", AutoModelForCausalLM, "microsoft/Phi-4-mini-instruct")
]

for model_name, ModelClass, tokenizer_name in model_list:
    print(f"Descargando y guardando el modelo: {model_name}")

    # Reemplazando "/" por "_" para evitar problemas con los nombres de los archivos
    safe_model_name = model_name.replace("/", "_")

    # Descargar y guardar el tokenizador desde el modelo base correspondiente
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    tokenizer.save_pretrained(os.path.join(BASE_DIR, "../tokenizer", safe_model_name))
    
    # Descargar y guardar el modelo con su tipo específico
    model = ModelClass.from_pretrained(model_name)
    model.save_pretrained(os.path.join(BASE_DIR, "../model", safe_model_name))

    print(f"Modelo {model_name} guardado en '../model/{safe_model_name}' y su tokenizador en '../tokenizer/{safe_model_name}'\n")
