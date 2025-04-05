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

def load_models():
    """Carga los modelos y tokenizadores en memoria."""
    global tokenizer_model_dict
    for model_name, ModelClass in model_path_list:
        print(f"Cargando modelo: {model_name}")
        try:
            tokenizer = AutoTokenizer.from_pretrained(os.path.join(TOKENIZER_GENERAL_PATH, model_name))
            model = ModelClass.from_pretrained(
                os.path.join(MODEL_GENERAL_PATH, model_name),
                device_map="auto",
                low_cpu_mem_usage=True
            )
            tokenizer_model_dict[model_name] = (tokenizer, model)
            print(f"Modelo {model_name} cargado correctamente.")
        except Exception as e:
            print(f"Error al cargar {model_name}: {e}")

def generate_response(model_name, text):
    """Genera una respuesta usando el nombre del modelo y un texto de entrada."""
    if model_name not in tokenizer_model_dict:
        return {"error": "Modelo no encontrado"}

    tokenizer, model = tokenizer_model_dict[model_name]
    inputs = tokenizer(text, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")

    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=50)

    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"response": response_text}