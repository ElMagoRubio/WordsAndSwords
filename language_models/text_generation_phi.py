from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

# Rutas locales donde están almacenados el modelo y el tokenizador
model_path = "./model/microsoft_Phi-3.5-mini-instruct"
tokenizer_path = "./tokenizer/microsoft_Phi-3.5-mini-instruct"

# Cargar el modelo y el tokenizador desde las carpetas locales
torch_dtype = torch.float16 if device == "cuda" else torch.float32
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

# Cargar el modelo directamente en la GPU si es posible
model = AutoModelForCausalLM.from_pretrained(
    model_path, 
    torch_dtype=torch_dtype, 
    device_map={"": device}  # Asignar el modelo entero a la GPU o CPU
)

# Definir el contexto y el prompt
context = "You are a medieval peasant called Phineas"
prompt = "What is your name?"

# Combinar contexto y prompt
input_text = f"Contexto: {context}\nPregunta: {prompt}"

# Tokenizar la entrada
inputs = tokenizer(input_text, return_tensors="pt")

# Mover los inputs al dispositivo correcto
inputs = {key: value.to(device) for key, value in inputs.items()}

# Generar la respuesta del modelo (asegurarse de generar solo una respuesta)
with torch.no_grad():
    outputs = model.generate(
        **inputs, 
        max_new_tokens=100, 
        pad_token_id=tokenizer.eos_token_id, 
        num_return_sequences=1, 
        eos_token_id=tokenizer.eos_token_id,  # Asegurarse de que el modelo termina cuando alcanza un EOS token
        do_sample=False  # No usar sampling, solo la respuesta más probable
    )

    # Decodificar la respuesta y recortar la parte del contexto y pregunta
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Recortar el contexto y la pregunta de la salida generada
    response = response.replace(f"Contexto: {context}\nPregunta: {prompt}\n", "")

# Mostrar solo la respuesta, sin mostrar el contexto anterior
print(response)
