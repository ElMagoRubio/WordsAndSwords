from transformers import AutoModelForCausalLM, AutoTokenizer
import os, time, torch

# Obtener la ruta absoluta del directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas locales del modelo y el tokenizador
model_path = os.path.join(BASE_DIR, "model/HuggingFaceTB_SmolLM2-360M-Instruct")
tokenizer_path = os.path.join(BASE_DIR, "tokenizer/HuggingFaceTB_SmolLM2-360M-Instruct")

# Cargar modelo y tokenizador
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

# Definir el contexto y la pregunta
context = "Responde como un aldeano medieval llamado Smol"

# Pregunta por entrada
prompt = input("Ingresa una pregunta que analizar: ").strip()

# Crear el input combinando contexto y pregunta
input_text = f"Context: {context}\nPrompt: {prompt}\nResponse:"  # Indica al modelo que debe generar una respuesta

# Tokenizar la entrada
inputs = tokenizer(input_text, return_tensors="pt")

# Inicio de medición del tiempo de generación de respuesta
start_time = time.time()

# Generar respuesta
with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=100
    )

# Decodificar la respuesta
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

# Calcular el tiempo de respuesta
total_time = time.time() - start_time

# Mostrar la respuesta y el tiempo de respuesta
print("\nRespuesta generada:")
print(response.replace(input_text, "").strip())  # Eliminamos el prompt para mostrar solo la respuesta
print(f"\nTiempo de respuesta: {total_time:.4f} segundos")
