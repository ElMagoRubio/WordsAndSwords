from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import os
import time
import torch
import sys

# Obtener la ruta absoluta del directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas locales del modelo y el tokenizador
model_path = os.path.join(BASE_DIR, "model/google_flan-t5-base")
tokenizer_path = os.path.join(BASE_DIR, "tokenizer/google_flan-t5-base")

# Cargar modelo y tokenizador
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

# Verificar que se recibió un argumento válido
if len(sys.argv) < 2:
    print("Error: No se recibió una pregunta como argumento.", flush=True)
    sys.exit(1)

# Obtener la pregunta desde los argumentos
prompt = sys.argv[1]

# Definir el contexto y crear la entrada
context = ("You are talking to your King. He will give you his name. Greet him like this: 'Hello, *name*, I'm here to serve your every need.'")

input_text = f"Context: {context}\nPrompt: {prompt}"

# Tokenizar la entrada
inputs = tokenizer(input_text, return_tensors="pt")

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
        repetition_penalty=1.5
    )

# Decodificar la respuesta
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

# Calcular el tiempo de respuesta
total_time = time.time() - start_time

# Imprimir solo la respuesta generada (sin texto adicional)
print(response, flush=True)
