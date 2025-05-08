import json
import os
import re
import time
import torch
import unicodedata
from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoModelForSequenceClassification, AutoTokenizer

# Obtener las rutas absolutas de modelos y tokenizadores
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_GENERAL_PATH = os.path.join(BASE_DIR, "../language_models/model")
TOKENIZER_GENERAL_PATH = os.path.join(BASE_DIR, "../language_models/tokenizer")

# Rutas de cada modelo
model_path_list = [
    ("lxyuan_distilbert-base-multilingual-cased-sentiments-student", AutoModelForSequenceClassification),
    ("google_flan-t5-large", AutoModelForSeq2SeqLM),
    ("HuggingFaceTB_SmolLM2-360M-Instruct", AutoModelForCausalLM)
]

# Diccionario con tokenizador y modelo.
tokenizer_model_dict = {}

# Detecta la emoción del texto de entrada del usuario
def detect_emotion(text):
    """Detecta la emoción en un texto usando el modelo de clasificación de emociones."""
    # Usar el primer modelo de la lista
    model_name = model_path_list[0][0]

    # Salir si el modelo no está cargado
    if model_name not in tokenizer_model_dict:
        return {"error": "Modelo de emociones no cargado"}

    # Cargar el modelo y tokenizador
    tokenizer, model = tokenizer_model_dict[model_name]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    # Preprocesar el texto y convertirlo en tensores
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(device)

    # Se analiza el texto
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.nn.functional.softmax(logits, dim=1).cpu().numpy()[0]

    # Obtener nombre de la clase predicha
    predicted_class_id = int(torch.argmax(logits, dim=1).item())
    predicted_label = model.config.id2label.get(predicted_class_id, str(predicted_class_id))

    if max(probs) < 0.5:
        label = "neutral"
    else:
        if predicted_label == "positive":
            label = "positiva"
        elif predicted_label == "negative":
            label = "negativa"
        else:
            label = predicted_label  # fallback

    return label

# Normaliza el texto, quitándole espacios, caracteres extraños y pasándolo a minúscula
def normalize_text(text):
    # Normalizar texto para eliminar tildes y caracteres raros
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')  # elimina caracteres no ASCII

    # Pasar a minúsculas
    text = text.lower()

    # Reemplazar cualquier espacio en blanco (espacios, tabulaciones, saltos) por _
    text = re.sub(r'\s+', '_', text)

    # Eliminar múltiples _ seguidos por uno solo
    text = re.sub(r'_+', '_', text)

    # Eliminar cualquier carácter que no sea letra, número o guion bajo
    text = re.sub(r'[^\w_]', '', text)

    # Eliminar _ al principio o al final si los hubiera
    text = text.strip('_')

    return text

# Construye el prompt completo, con la instrucción, emoción buscada, contexto e historial conversacional.
def build_prompt(text, task_description, emotion, char_name, char_description, context_tokens, context_dict, history, model_name="google_flan-t5-large"):
    print(f"\nConstruyendo prompt para {model_name}...")

    # Adición de tokens a contexto
    context_section = ""
    for token_key in context_tokens:
        context_section += f"\t\n{token_key}: {context_dict[token_key]}\n"

    # print(f"Explicación de los contextos: {context_section}")

    # Historial formateado
    history_section = ""
    if model_name == "google_flan-t5-large":
        for user_input, char_response in history:
            history_section += f"[user]: {user_input}\n[{char_name}]: {char_response}\n\n"
    elif model_name == "HuggingFaceTB_SmolLM2-360M-Instruct":
        for user_input, char_response in history:
            history_section += f"[user]: {user_input}\n[{char_name}]: {char_response}\n\n"

    # print(f"Historial de conversación: {history_section}")

    # Ensamblado final del prompt según el modelo
    if model_name == "google_flan-t5-large":
        prompt = (
            f"Tarea: {task_description}"
            f"\n\nResponde de manera {emotion}"
            f"\n\nPersonaje:\nNombre: {char_name}\nDescripción: {char_description}"
            f"\n\nContexto:\n{context_section}"
            f"\n\nHistorial:\n{history_section}"
            f"[user]: {text}\n[{char_name}]:"
        )
    elif model_name == "HuggingFaceTB_SmolLM2-360M-Instruct":
        prompt = (
            f"[system]: Tarea: {task_description}"
            f"\n\n[system]: Responde de manera {emotion}"
            f"\n\n[system]: Personaje:\nNombre: {char_name}\nDescripción: {char_description}"
            f"\n\n[system]: Contexto:{context_section}"
            f"\n\n{history_section}"
            f"[user]: {text}\n[{char_name}]:"
        )
    else:
        raise ValueError("Modelo no soportado.")

    print(f"Prompt: {prompt}")
    return prompt

# Añade el contexto al personaje.
def add_context(text, context_tokens, token_list, context_dict):
    # print(f"\nAñadiendo contexto...")
    # print(f"\n\nLista de tokens: {token_list}")
    # print(f"\n\nDiccionario de contexto: {context_dict}")
    normalized_text = normalize_text(text)

    # Buscamos los tokens normalizados dentro del texto normalizado
    for token_key, token_value in token_list.items():
        # print(f"\n\nEvaluando token: {token_value}")
        if token_key in normalized_text:
                # print(f"\n\nEncontrado token {token_value} en el texto.")
                if token_value in context_dict and token_value not in context_tokens:
                    # print(f"Añadiendo entrada {token_value}...")
                    context_tokens.append(token_value)
                    # print(f"\n\nToken {token_value} añadido")

    # print(f"\n\nEvaluación finalizada, contexto añadido: {context_tokens}")
    return context_tokens

# Genera la respuesta dado un modelo y un prompt.
def generate_response(model_name, text):
    """Genera una respuesta usando el nombre del modelo y un texto de entrada."""
    if model_name not in tokenizer_model_dict:
        return {"error": "Modelo no encontrado"}

    tokenizer, model = tokenizer_model_dict[model_name]
    inputs = tokenizer(text, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")

    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=100)

    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return response_text

# Sanea la respuesta para sólo mostrar lo que dice el personaje
def process_response(texto, char_name):
    patron = rf"\[{re.escape(char_name)}\]:\s*(.*)"
    coincidencia = re.search(patron, texto)
    if coincidencia:
        return coincidencia.group(1)
    return None

# Devuelve los modelos tras cargarlos
def get_models():
    load_models()
    print(f"Tokenizer keys: {tokenizer_model_dict.keys()}")
    return list(tokenizer_model_dict.keys())

# Mide cuánto tarda en generarse una respuesta.
def measure_generation_time(model_name, text):
    """Mide el tiempo que tarda en generarse una respuesta con un modelo dado."""
    if model_name not in tokenizer_model_dict:
        return {"error": "Modelo no encontrado"}

    tokenizer, model = tokenizer_model_dict[model_name]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    inputs = tokenizer(text, return_tensors="pt").to(device)

    # Medir el tiempo de generación
    start_time = time.time()

    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=50)

    end_time = time.time()
    generation_time = end_time - start_time

    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {
        "response": response_text,
        "time_seconds": generation_time
    }

# Abre archivos .json a partir de una ruta
def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# Carga los modelos de lenguaje
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
