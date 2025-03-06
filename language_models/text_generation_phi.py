from transformers import Phi3ForCausalLM, AutoTokenizer, pipeline
import gc, os, time, torch

# Obtener la ruta absoluta del directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas locales del modelo y el tokenizador
model_path = os.path.join(BASE_DIR, "model/microsoft_Phi-3.5-mini-instruct")
tokenizer_path = os.path.join(BASE_DIR, "tokenizer/microsoft_Phi-3.5-mini-instruct")

# Cargar modelo en GPU con dtype automático y código remoto confiable
model = Phi3ForCausalLM.from_pretrained(
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
    "max_new_tokens": 100,
    "return_full_text": False,
    "temperature": 0.5,
    "do_sample": True,
}

# Mensajes ajustados para obtener solo la respuesta sin generar preguntas adicionales
messages = [
    {"role": "system", "content": "Eres un aldeano medieval llamado Phineas. Te diriges a tu rey. La respuesta debe ser concisa y tener menos de 100 tokens."},
    {"role": "user", "content": "Cuál es tu oficio, Phineas?"},  # Aquí se define la pregunta directa
]

# Convertir mensajes a texto
input_text = "\n".join([msg["content"] for msg in messages])

# Medir tiempo de respuesta
if torch.cuda.is_available():
    torch.cuda.synchronize()
    start_time = torch.cuda.Event(enable_timing=True)
    end_time = torch.cuda.Event(enable_timing=True)
    start_time.record()
else:
    start_time = time.time()

with torch.inference_mode():  # Más eficiente que no_grad()
    output = pipe(input_text, **generation_args)
    response = output[0]['generated_text']

if torch.cuda.is_available():
    end_time.record()
    torch.cuda.synchronize()
    elapsed_time = start_time.elapsed_time(end_time) / 1000  # Tiempo en s
else:
    elapsed_time = time.time() - start_time  # Medición en CPU

# Liberar memoria de GPU y CPU para evitar acumulación y fragmentación
torch.cuda.empty_cache()
torch.cuda.ipc_collect()
gc.collect()

# Mostrar la respuesta y el tiempo de respuesta
print(f"Respuesta generada: {response}")
print(f"Tiempo de respuesta: {elapsed_time:.4f} s")
