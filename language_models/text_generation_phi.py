from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import gc, os, sys, time, torch

if (len(sys.argv) != 2):
    print("ERROR: Número de argumentos incorrecto.\nFormato: (./text_generation_phi.py) (texto_entrada_usuario)")
    exit(1)

# Obtener la ruta absoluta del directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas locales del modelo y el tokenizador
model_path = os.path.join(BASE_DIR, "model/microsoft_Phi-4-mini-instruct")
tokenizer_path = os.path.join(BASE_DIR, "tokenizer/microsoft_Phi-4-mini-instruct")

# Cargar modelo en GPU con dtype automático y código remoto confiable
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    device_map="auto",
    torch_dtype="auto",
    trust_remote_code=True
)

# Si se usa PyTorch 2.0+, compilamos el modelo para mayor eficiencia en GPU
if torch.__version__ >= "2.0":
    model = torch.compile(model)

# Cargar tokenizador
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

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
