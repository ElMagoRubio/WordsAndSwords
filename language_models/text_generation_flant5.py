from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

# Rutas locales donde están almacenados el modelo y el tokenizador
model_path = "./model/google_flan-t5-base"
tokenizer_path = "./tokenizer/google_flan-t5-base"

# Cargar el modelo y el tokenizador desde las carpetas locales
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

# Definir el prompt y contexto
context = "You are a medieval peasant called Emerick"
prompt = "And what is thy name, servant?"

input_text = f"Contexto: {context} Pregunta: {prompt}"

# Tokenizar la entrada
inputs = tokenizer(input_text, return_tensors="pt")

# Generar la respuesta del modelo
with torch.no_grad():
    outputs = model.generate(**inputs, max_length=100)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

# Mostrar la respuesta
print("Contexto:", context)
print("Pregunta:", prompt)
print("Respuesta:", response)
