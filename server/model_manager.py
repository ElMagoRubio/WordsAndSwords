import json, os, re, time, torch, unicodedata
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoModelForSequenceClassification, AutoTokenizer

# Obtener las rutas absolutas de modelos y tokenizadores
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_GENERAL_PATH = os.path.join(BASE_DIR, "../language_models/model")
TOKENIZER_GENERAL_PATH = os.path.join(BASE_DIR, "../language_models/tokenizer")


# Rutas de cada modelo, tipo de modelo y tokenizador
model_list = [
    ("lxyuan_distilbert-base-multilingual-cased-sentiments-student", AutoModelForSequenceClassification, "lxyuan_distilbert-base-multilingual-cased-sentiments-student"), 
    ("google_flan-t5-large", AutoModelForSeq2SeqLM, "google_flan-t5-large"),
    ("ElMagoRubio_flan-t5-large-lora", AutoModelForSeq2SeqLM, "google_flan-t5-large"),
    ("HuggingFaceTB_SmolLM2-360M-Instruct", AutoModelForCausalLM, "HuggingFaceTB_SmolLM2-360M-Instruct"),
    ("ElMagoRubio_SmolLM2-360M-Instruct-lora", AutoModelForCausalLM, "HuggingFaceTB_SmolLM2-360M-Instruct")
]
# Diccionario con tokenizador y modelo.
tokenizer_model_dict = {}

# Abre archivos .json a partir de una ruta
def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# Rango de emociones
emotion_range = load_json(os.path.join(BASE_DIR, f"../assets/character_sheets/emotion_levels.json"))

# Detecta la emoción del texto de entrada del usuario
def detect_emotion(text):
    """Detecta la emoción en un texto usando el modelo de clasificación de emociones."""
    # Usar el primer modelo de la lista
    model_name = model_list[0][0]

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
def build_prompt(text, task_description, emotion, char_name, char_description, context_tokens, context_dict, history, model_name="ElMagoRubio_SmolLM2-360M-Instruct-lora", debug_mode=False):
    print(f"\nEntrada a la función de construcción de prompt mediante el modelo {model_name}...")

    # Adición de tokens a contexto
    context_section = ""
    for token_key in context_tokens:
        context_section += f"\n\t{token_key}: {context_dict[token_key]}\n"

    if (debug_mode):
        print(f"Explicación de los contextos: {context_section}")

    # Historial formateado
    history_section = ""
    if "flan-t5-large" in model_name:
        for user_input, char_response in history:
            history_section += f"[user]: {user_input}\n[{char_name}]: {char_response}\n\n"
    elif "SmolLM2-360M-Instruct" in model_name:
        for user_input, char_response in history:
            history_section += f"\t<|user|>: {user_input}\n\t<|assistant|>[{char_name}]: {char_response}\n\n"

    if (debug_mode):
        print(f"Historial de conversación: {history_section}")

    # Ensamblado final del prompt según el modelo

    print(f"Construyendo prompt...")
    if model_name == "google_flan-t5-large" or "flan-t5-finetuned_v1":
        prompt = (
            f"Tarea: {task_description}"
            f"\n\nNivel de emocion: {emotion} ({emotion_range[str(emotion)]})"
            f"\n\nDatos del personaje:\n\tNombre: {char_name}\n\tDescripción: {char_description}"
            f"\n\nContexto:\n{context_section}"
            f"\t[user]: {text}\n\t[{char_name}]: "
        )
    elif model_name == "HuggingFaceTB_SmolLM2-360M-Instruct" or "smol-finetuned-v1":
        prompt = (
            f"<|system|> Tarea: {task_description}"
            f"\n\nNivel de emocion: {emotion} ({emotion_range[emotion+5]})"
            f"\n\nDatos del personaje:\nNombre: {char_name}\nDescripción: {char_description}"
            f"\n\nContexto:{context_section}"
            f"\n\n{history_section}"
            f"\t<|user|> {text}\n\t<|assistant|> [{char_name}]: "
        )
    else:
        raise ValueError("Modelo no soportado.")

    if (debug_mode):
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
    device = next(model.parameters()).device
    inputs = tokenizer(text, return_tensors="pt").to(device)

    eos_token_id = tokenizer.eos_token_id
    if eos_token_id is None:
        eos_token_id = tokenizer.pad_token_id

    try:
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=True,
                temperature=0.8,
                top_p=0.9,
                repetition_penalty=1.2,
                eos_token_id=eos_token_id,
            )

        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response_text

    except Exception as e:
        return {"error": f"Error en la generación: {str(e)}"}

# Sanea la respuesta para sólo mostrar lo que dice el personaje
def process_response(text, char_name):
    pattern = rf"\[{re.escape(char_name)}\]:\s*((?:[^\[]|\[(?![^\]]+\]))+)"
    matches = re.findall(pattern, text)
    if matches:
        return matches[-1]  # Última coincidencia
    return text

# Devuelve los modelos tras cargarlos
def get_models(model_list=model_list):
    load_models(model_list)
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

# Carga los modelos de lenguaje
def load_models(model_list=model_list):
    """Carga los modelos y tokenizadores en memoria, incluyendo adaptadores LoRA."""
    global tokenizer_model_dict
    for model_name, ModelClass, base_tokenizer in model_list:
        print(f"Cargando modelo: {model_name}")

        try:
            tokenizer_path = os.path.normpath(os.path.join(TOKENIZER_GENERAL_PATH, base_tokenizer))
            model_path = os.path.normpath(os.path.join(MODEL_GENERAL_PATH, model_name))
            tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=True)

            if model_name.endswith("-lora"):
                # Derivar nombre del modelo base eliminando el sufijo "-lora"
                base_model_name = base_tokenizer
                base_model_path = os.path.normpath(os.path.join(MODEL_GENERAL_PATH, base_model_name))

                if ModelClass is None:
                    raise ValueError(f"No se ha especificado la clase del modelo base para {model_name}")


                # Cargar modelo base usando la clase especificada en model_list
                base_model = ModelClass.from_pretrained(
                    base_model_path,
                    device_map="cuda" if torch.cuda.is_available() else "cpu",
                    low_cpu_mem_usage=True,
                    local_files_only=True
                )

                # Aplicar adaptador LoRA
                model = PeftModel.from_pretrained(base_model, model_path)
                model.to("cuda" if torch.cuda.is_available() else "cpu")

            else:
                model = ModelClass.from_pretrained(
                    model_path,
                    device_map="cuda" if torch.cuda.is_available() else "cpu",
                    offload_buffers=True,
                    low_cpu_mem_usage=True,
                    local_files_only=True                    
                )

            tokenizer_model_dict[model_name] = (tokenizer, model)
            print(f"Modelo {model_name} cargado correctamente.\n")

        except Exception as e:
            print(f"Error al cargar {model_name}: {e}")
            