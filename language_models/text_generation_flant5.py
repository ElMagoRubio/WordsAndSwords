from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import os, time, torch

# Obtener la ruta absoluta del directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas locales del modelo y el tokenizador
model_path = os.path.join(BASE_DIR, "model/google_flan-t5-base")
tokenizer_path = os.path.join(BASE_DIR, "tokenizer/google_flan-t5-base")

# Cargar modelo y tokenizador
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

# Definir el contexto y la pregunta
context = ("You must take the role of Flanagan, a medieval peasant talking to his king. "
           "Flanagan speaks in a respectful manner, in a humble and ancient tone. "
           "Flanagan ends his sentences with ', your majesty'")
prompt = "[King]: Tell me, Flanagan, what is your craft?"

# Crear el input combinando contexto y pregunta
input_text = f"Context: {context}\nPrompt: {prompt}"

# Tokenizar la entrada
inputs = tokenizer(input_text, return_tensors="pt")

total_time = 0

start_time = time.time()
    
with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_length=100,
        do_sample=True,
        temperature=0.9,
        top_p=0.92,
        repetition_penalty=1.2
    )

# Decodificar la respuesta
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

end_time = time.time()
total_time += (end_time - start_time)

# Mostrar la respuesta y el tiempo medio
print(f"Respuesta generada: {response}")
print(f"Tiempo medio por respuesta: {total_time:.4f} segundos")
