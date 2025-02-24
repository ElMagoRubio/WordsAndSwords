from transformers import AutoModelForQuestionAnswering, AutoTokenizer
import torch

# Rutas locales donde están almacenados el modelo y el tokenizador
model_path = "./model/deepset_tinyroberta-squad2"
tokenizer_path = "./tokenizer/deepset_tinyroberta-squad2"

# Cargar el modelo y el tokenizador desde las carpetas locales
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
model = AutoModelForQuestionAnswering.from_pretrained(model_path)

# Definir el prompt (pregunta) y el contexto
context = "El Sol es una estrella situada en el centro del sistema solar. Su luz tarda aproximadamente 8 minutos en llegar a la Tierra."
prompt = "¿Cuánto tarda la luz del Sol en llegar a la Tierra?"

# Tokenizar la entrada
inputs = tokenizer(prompt, context, return_tensors="pt")

# Obtener la respuesta del modelo
with torch.no_grad():
    outputs = model(**inputs)
    answer_start = torch.argmax(outputs.start_logits)
    answer_end = torch.argmax(outputs.end_logits) + 1
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end]))

# Mostrar la respuesta
print("Contexto:", context)
print("Pregunta:", prompt)
print("Respuesta:", answer)