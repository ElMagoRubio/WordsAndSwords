import os
import torch
from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoModelForSequenceClassification, AutoTokenizer

# Obtener las rutas absolutas de modelos y tokenizadores
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_GENERAL_PATH = os.path.join(BASE_DIR, "model")
TOKENIZER_GENERAL_PATH = os.path.join(BASE_DIR, "tokenizer")

# Rutas de cada modelo
model_path_list = [
    ("lxyuan_distilbert-base-multilingual-cased-sentiments-student", AutoModelForSequenceClassification),
    ("google_flan-t5-large", AutoModelForSeq2SeqLM),
    ("HuggingFaceTB_SmolLM2-360M-Instruct", AutoModelForCausalLM),
    ("microsoft_Phi-4-mini-instruct", AutoModelForCausalLM)
]

# Diccionario con tokenizador y modelo.
tokenizer_model_dict = {}

# Cargar tokenizador y model para cada ruta
for model_name, ModelClass in model_path_list:
    print("Cargando modelo: " + model_name)

    try:
        # Cargar tokenizador correspondiente al modeloactual
        tokenizer = AutoTokenizer.from_pretrained(os.path.join(TOKENIZER_GENERAL_PATH, model_name))
        # Cargar modelo correspondiente
        model = ModelClass.from_pretrained(
            os.path.join(MODEL_GENERAL_PATH, model_name), 
            device_map="auto",
            low_cpu_mem_usage=True
        )

        #Almacenar tokenizador y modelo en diccionario
        tokenizer_model_dict[model_name] = (tokenizer, model)
        print("Modelo y tokenizador cargado con éxito.")
    
    except Exception as e:
        print(f"Error al cargar {model_name}: {e}")

# Devolver el tokenizador y modelo correspondiente a partir de un índice
def get_model_and_tokenizer_from_index(index):
    if index < 0 or index >= len(model_path_list):
        raise IndexError("Índice fuera de rango")
    
    model_name = model_path_list[index][0]
    return tokenizer_model_dict[model_name]
