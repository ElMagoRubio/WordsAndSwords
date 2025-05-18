import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import os, traceback

# Rutas locales del modelo y tokenizer
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_name = "google_flan-t5-large"
tokenizer_path = os.path.join(BASE_DIR, f"./tokenizer/{model_name}")
model_path = os.path.join(BASE_DIR, f"./model/{model_name}")

# Cargar tokenizer y modelo
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to("cuda" if torch.cuda.is_available() else "cpu")

# Crear entrada de prueba
text_input = "Adopta el rol de un personaje y responde de forma coherente."
inputs = tokenizer([text_input], return_tensors="pt", padding="max_length", truncation=True, max_length=512)

device = "cuda" if torch.cuda.is_available() else "cpu"
inputs = {k: v.to(device) for k, v in inputs.items()}

# Probar batch sizes
max_batch = 1
success = True

print("🔍 Probando batch sizes...\n")

while success:
    try:
        torch.cuda.reset_peak_memory_stats()
        batch_inputs = {k: v.repeat(max_batch, 1) for k, v in inputs.items()}

        with torch.no_grad():
            model.generate(**batch_inputs, max_new_tokens=10)

        allocated = torch.cuda.memory_allocated() / (1024 ** 2)  # MB
        peak = torch.cuda.max_memory_allocated() / (1024 ** 2)   # MB

        print(f"Batch size {max_batch} OK | Memoria usada: {allocated:.2f} MB | Pico: {peak:.2f} MB")

        max_batch += 1

    except RuntimeError as e:
        if "out of memory" in str(e):
            print(f"Batch size {max_batch} excede la memoria de la GPU.")
            success = False
        else:
            print("Otro error ocurrió:")
            traceback.print_exc()
            break
    finally:
        torch.cuda.empty_cache()

print(f"\nTamaño de batch máximo recomendado: {max_batch - 1}")
