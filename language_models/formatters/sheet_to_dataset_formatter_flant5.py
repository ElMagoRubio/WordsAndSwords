import json
import os, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(BASE_DIR, "../datasets/finetuning_ready_dataset_1_flant5.jsonl", )

json_files = []
for i in range(1, len(sys.argv)):
    json_files.append(os.path.join(BASE_DIR, "../../assets/character_sheets", sys.argv[i]))

dataset = []

for json_file in json_files:
    print(json_file)
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    
    for entry in data:
        tarea = entry["Tarea"]
        nivel_emocion = entry["Nivel de emoción"]
        emocion = nivel_emocion.split('(')[-1].replace(')', '').strip()
        personaje = entry["Datos del personaje"]["Nombre"]
        descripcion_personaje = entry["Datos del personaje"]["Descripción"]
        contexto = entry["Contexto"]
        historial = entry["Historial"]
        prompt_usuario = entry["Prompt del usuario"]
        respuesta = entry["Respuesta"]

        # Crear el input
        input_data = f"Tarea: {tarea}\n\nNivel de emocion: {nivel_emocion}\n\nDatos del personaje:\n\tNombre: {personaje}\n\tDescripción del personaje: {descripcion_personaje}\n\nContexto:\n"
        
        for token, descripcion in contexto.items():
            input_data += f"\t{token}: {descripcion}\n"
        
        # Crear el historial en formato adecuado
        historial_data = ""
        for key, value in historial.items():
            historial_data += f"\t{key}: {value}\n"
        
        input_data += f"\nHistorial:\n{historial_data}\n{prompt_usuario}"

        #print(f"input: {input_data}\ntarget: {respuesta}")
        dataset.append({"input": input_data, "target": respuesta})

print(len(dataset))
print(f"\n\n{dataset[0]}")
print(f"\n\n{dataset[110]}")
print(f"\n\n{dataset[220]}")
print(f"\n\n{dataset[330]}")
print(f"\n\n{dataset[440]}")
print(f"\n\n{dataset[549]}")

with open(output_file, 'w', encoding='utf-8') as file:
    for entry in dataset:
        json.dump(entry, file, ensure_ascii=False)
        file.write("\n")


