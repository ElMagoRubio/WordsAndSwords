import gc, os, sys, time, torch, csv
from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoModelForSequenceClassification

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from server import model_manager as model

torch.cuda.empty_cache()
gc.collect()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_list = [
    ("tabularisai_multilingual-sentiment-analysis", AutoModelForSequenceClassification, "tabularisai_multilingual-sentiment-analysis"),
    ("lxyuan_distilbert-base-multilingual-cased-sentiments-student", AutoModelForSequenceClassification, "lxyuan_distilbert-base-multilingual-cased-sentiments-student"), 
    ("google_flan-t5-large", AutoModelForSeq2SeqLM, "google_flan-t5-large"),
    ("microsoft_Phi-4-mini-instruct", AutoModelForCausalLM, "microsoft_Phi-4-mini-instruct"),
    ("HuggingFaceTB_SmolLM2-360M-Instruct", AutoModelForCausalLM, "HuggingFaceTB_SmolLM2-360M-Instruct"),
]

if len(sys.argv) != 2:
    raise ValueError("ERROR: Número de argumentos incorrecto.\nFormato: (./time_measurement.py) (modelo)")

model_name = sys.argv[1]
allowed_model_names = [name for name, _, _ in model_list]

if model_name not in allowed_model_names:
    raise ValueError(
        "ERROR: Nombre de modelo incorrecto.\n\nModelos disponibles:\n" +
        "\n".join(allowed_model_names)
    )

# Carga de modelos
model.load_models([m for m in model_list if m[0] == model_name])

if model_name not in model.tokenizer_model_dict:
    raise ValueError(f"ERROR: El modelo '{model_name}' no fue cargado correctamente.")

tokenizer, loaded_model = model.tokenizer_model_dict[model_name]
device = "cuda" if torch.cuda.is_available() else "cpu"
loaded_model.to(device)

context = "Actúa como un aldeano medieval llamado X. Estás hablando con tu rey. Finaliza tus respuestas con ', su majestad'"
prompt = "¿Cuál es tu nombre plebeyo?"
full_prompt = f"{context}\n{prompt}"

inference_times = []
print(f"\nRealizando pruebas con el modelo: {model_name}\n")
print(f"Clase del modelo detectada: {loaded_model.__class__.__name__}")

for i in range(50):
    print(f"Iteración {i+1}/50")

    if ("ForSequenceClassification" in loaded_model.__class__.__name__):
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True).to(device)
        start = time.time()
        with torch.no_grad():
            outputs = loaded_model(**inputs)
        end = time.time()
        logits = outputs.logits
        predicted_class_id = int(torch.argmax(logits, dim=1).item())
        label = loaded_model.config.id2label.get(predicted_class_id, str(predicted_class_id))
        print(f"Tiempo: {end - start:.3f}s | Clase predicha: {label}")

    elif ("ForCausalLM" in loaded_model.__class__.__name__ or "ForConditionalGeneration" in loaded_model.__class__.__name__):
        inputs = tokenizer(full_prompt, return_tensors="pt").to(device)
        generate_kwargs = {
            "max_new_tokens": 100,
            "do_sample": True,
            "temperature": 0.8,
            "top_p": 0.9,
            "repetition_penalty": 1.2,
            "eos_token_id": tokenizer.eos_token_id or tokenizer.pad_token_id,
        }
        start = time.time()
        with torch.no_grad():
            outputs = loaded_model.generate(**inputs, **generate_kwargs)
        end = time.time()
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Tiempo: {end - start:.3f}s | Respuesta: {response[:80]}...")

    elif ("ForSeq2SeqLM" in loaded_model.__class__.__name__):
        inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True, padding=True).to(device)
        start = time.time()
        with torch.no_grad():
            outputs = loaded_model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=True,
                temperature=0.8,
                top_p=0.9,
                repetition_penalty=1.2,
                eos_token_id=tokenizer.eos_token_id or tokenizer.pad_token_id,
            )
        end = time.time()
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Tiempo: {end - start:.3f}s | Respuesta: {response[:80]}...")

    else:
        print("Modelo no compatible con este script.")
        break

    inference_times.append(end - start)

# Cálculo y almacenamiento de resultados
if inference_times:
    avg_time = sum(inference_times) / len(inference_times)
    print(f"\nTiempo medio de inferencia con {model_name}: {avg_time:.3f} segundos")

    safe_model_name = model_name.replace("/", "_")

    output_csv = os.path.join(BASE_DIR, f"times_{safe_model_name}.csv")
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Iteración", "Tiempo (segundos)"])
        for i, t in enumerate(inference_times, 1):
            writer.writerow([i, f"{t:.6f}"])
    print(f"Archivo CSV guardado en {output_csv}")
else:
    print("No se generaron tiempos válidos.")
