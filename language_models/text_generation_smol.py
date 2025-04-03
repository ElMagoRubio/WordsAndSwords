from llm_loader import get_model_and_tokenizer_from_index
import sys, time, torch

if (len(sys.argv) != 2):
    print("ERROR: Número de argumentos incorrecto.\nFormato: (./text_generation_smol.py) (texto_entrada_usuario)")
    exit(1)

# Cargar modelo y tokenizador
tokenizer, model = get_model_and_tokenizer_from_index(2)

# Definir el contexto y la pregunta
context = "Responde como un aldeano medieval llamado Smol. Genera una sola respuesta de menos de 50 palabras en español."

# Pregunta por entrada
prompt = sys.argv[1].strip()

# Crear el input combinando contexto y pregunta
input_text = f"Contexto: {context}\nPrompt: {prompt}\nRespuesta:"  # Indica al modelo que debe generar una respuesta

# Tokenizar la entrada
inputs = tokenizer(input_text, return_tensors="pt")

# Inicio de medición del tiempo de generación de respuesta
start_time = time.time()

# Generar respuesta
with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=50,
        do_sample=False
    )

# Decodificar la respuesta
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

# Calcular el tiempo de respuesta
total_time = time.time() - start_time

# Mostrar la respuesta y el tiempo de respuesta
print("\nRespuesta generada:")
print(response.replace(input_text, "").strip())  # Eliminamos el prompt para mostrar solo la respuesta
print(f"\nTiempo de respuesta: {total_time:.4f} segundos")
