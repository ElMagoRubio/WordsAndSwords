import json
import sys
import os
from copy import deepcopy

# Se validan los argumentos
if (len(sys.argv) != 2):
    raise ValueError(f"ERROR: Número de argumentos incorrecto.\nFormato: (./extended_data_generator.py) (nombre_archivo_dataset.json (sin ruta))")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(BASE_DIR, "../assets/character_sheets", sys.argv[1])
print(f"Ruta del dataset original: {dataset_path}")

# Cargar archivo de niveles emocionales
emotion_levels_path = os.path.join(BASE_DIR, "../assets/character_sheets", "emotion_levels.json")
with open(emotion_levels_path, "r", encoding="utf-8") as f:
    emotion_labels = json.load(f)

# Mapear niveles de -5 a 5 con sus etiquetas
emotion_map = {i - 5: label for i, label in enumerate(emotion_labels)}
print(f"\n\nEmotion map: {emotion_map}\n")

# Cargar prompts de tarea
prompts_path = os.path.join(BASE_DIR, "../assets/character_sheets", "prompts.json")
with open(prompts_path, "r", encoding="utf-8") as f:
    task_prompts = json.load(f)

print(f"\n\nTask prompts: {task_prompts}\n")

# Cargar dataset original
with open(dataset_path, "r", encoding="utf-8") as f:
    original_data = json.load(f)

extended_data = []

for entry in original_data:    
    for level in range(-5, 6):
        if level == 0:
            extended_data.append(entry)
            continue  # Saltar el nivel neutral ya que ya existe
        
        new_entry = deepcopy(entry)
        new_entry["Nivel de emoción"] = f"{str(level)} ({emotion_map[level]})"
        # Descripción de tarea según el nivel emocional
        if level == -5:
            new_entry["Tarea"] = task_prompts["EMOTION_LOWER_THRESHOLD"]
        elif level == 5:
            new_entry["Tarea"] = task_prompts["EMOTION_UPPER_THRESHOLD"]
        else:
            new_entry["Tarea"] = task_prompts["DEFAULT_PROMPT"]
        # Vaciar respuesta
        new_entry["Respuesta"] = ""
        print(f"\n{new_entry}\n")

        extended_data.append(new_entry)
        

# Nombre del archivo de salida
base, ext = os.path.splitext(dataset_path)
output_path = f"{base}_extended{ext}"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(extended_data, f, ensure_ascii=False, indent=2)

print(f"Variaciones generadas: {len(extended_data)}")
print(f"Archivo guardado en: {output_path}")
