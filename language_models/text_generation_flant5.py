from llm_loader import get_model_and_tokenizer_from_index
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import os, sys, time, torch

if (len(sys.argv) != 2):
    print("ERROR: Número de argumentos incorrecto.\nFormato: (./text_generation_flant5.py) (texto_entrada_usuario)")
    exit(1)

# Detectar si hay GPU disponible
device = "cuda" if torch.cuda.is_available() else "cpu"

# Cargar modelo y tokenizador
tokenizer, model = get_model_and_tokenizer_from_index(1)

context = "Responde como un aldeano medieval llamado Flanagan."

# Obtener la pregunta desde los argumentos
prompt = sys.argv[1].strip()

input_text = f"Context: {context}\nPrompt: {prompt}"

# Tokenizar la entrada
inputs = tokenizer(input_text, return_tensors="pt").to(device)

# Inicio de medición del tiempo de generación de respuesta
start_time = time.time()

# Generar respuesta
with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=100,
        do_sample=True,
        temperature=1.0,
        top_p=0.92,
        repetition_penalty=1.0
    )

# Decodificar la respuesta
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

# Calcular el tiempo de respuesta
total_time = time.time() - start_time

# Imprimir solo la respuesta generada (sin texto adicional)
print(response, flush=True)
sys.stdout.flush()
