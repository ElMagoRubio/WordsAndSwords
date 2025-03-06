from transformers import AutoModelForQuestionAnswering, AutoTokenizer
import os, time, torch

# Obtener la ruta absoluta del directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas locales del modelo y el tokenizador
model_path = os.path.join(BASE_DIR, "model/deepset_tinyroberta-squad2")
tokenizer_path = os.path.join(BASE_DIR, "tokenizer/deepset_tinyroberta-squad2")

# Cargar el modelo y el tokenizador desde las carpetas locales
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
model = AutoModelForQuestionAnswering.from_pretrained(model_path)

# Definir el prompt (pregunta) y el contexto
context = "You are a medieval peasant called Robert. You must answer to your king. End each utterance with ', your Majesty'."
prompt = "What is your craft?"

# Tokenizar la entrada
inputs = tokenizer(prompt, context, return_tensors="pt")

start_time = time.time()
with torch.no_grad():
    outputs = model(**inputs)
    answer_start = torch.argmax(outputs.start_logits)
    answer_end = torch.argmax(outputs.end_logits) + 1
    answer = tokenizer.convert_tokens_to_string(
        tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end])
    )

# Decodificar la respuesta
response = tokenizer.convert_tokens_to_string(
    tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end])
)

#Calcular el tiempo de respuesta
total_time = time.time() - start_time

# Mostrar la respuesta y el tiempo de respuesta
print(f"Respuesta generada: {response}")
print(f"Tiempo de respuesta: {total_time:.4f} segundos")
