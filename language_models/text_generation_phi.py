from llm_loader import get_model_and_tokenizer_from_index
from transformers import pipeline
import gc, os, sys, time, torch

if (len(sys.argv) != 2):
    print("ERROR: Número de argumentos incorrecto.\nFormato: (./text_generation_phi.py) (texto_entrada_usuario)")
    exit(1)

# Rutas locales del modelo y el tokenizador
tokenizer, model = get_model_and_tokenizer_from_index(3)

print(f"Modelo: {model}")
print(f"Tokenizador: {tokenizer}")

# Crear pipeline una sola vez
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer
)

generation_args = {
    "max_new_tokens": 50,  # Reducimos la longitud máxima
    "return_full_text": False,
    "temperature": 0.3,  # Más bajo para respuestas más precisas
    "do_sample": True,   # Desactiva sampling para respuestas más controladas
}

# Mensaje ajustado al formato del modelo
#input_text = f"<|user|>\nCuál es tu oficio, Phineas?\n<|assistant|>"

# Introducir entrada de texto
input_text = sys.argv[1].strip()
input_text = f"<|user|>\n{input_text}\n<|assistant|>"


# Medir tiempo de respuesta
if torch.cuda.is_available():
    torch.cuda.synchronize()
    start_time = torch.cuda.Event(enable_timing=True)
    end_time = torch.cuda.Event(enable_timing=True)
    start_time.record()
else:
    start_time = time.time()

with torch.inference_mode():
    output = pipe(input_text, **generation_args)
    response = output[0]['generated_text'].strip()

# Filtrar la respuesta para evitar generación adicional
response = response.split("\n")[0]  # Cortamos en la primera línea para evitar que genere preguntas

if torch.cuda.is_available():
    end_time.record()
    torch.cuda.synchronize()
    elapsed_time = start_time.elapsed_time(end_time) / 1000
else:
    elapsed_time = time.time() - start_time

# Liberar memoria de GPU y CPU
torch.cuda.empty_cache()
torch.cuda.ipc_collect()
gc.collect()

# Mostrar la respuesta y el tiempo de respuesta
print(f"Respuesta generada: {response}")
print(f"Tiempo de respuesta: {elapsed_time:.4f} s")
