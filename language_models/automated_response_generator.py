from copy import deepcopy
from openai import OpenAI
import json, os, sys

#Creamos un cliente para comunicar con el servidor de openAI, pasando la clave

print (os.getenv("OPENAI_API_KEY"))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-3.5-turbo"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Se validan los argumentos
if (len(sys.argv) != 2):
    raise ValueError(f"ERROR: Número de argumentos incorrecto.\nFormato: (./automated_response_generator.py) (nombre_personaje)")

char_name = sys.argv[1]

template_dataset_path = os.path.join(BASE_DIR, f"../assets/character_sheets/finetuning_{char_name}_extended_template.json")

with open(template_dataset_path, "r", encoding="utf-8") as f:
    template_dataset = json.load(f)

#Se guarda el bloque de variaciones de ejemplo del archivo, las 11 primeras (corresponden a una entrada con todas sus variaciones emocionales)
variation_example_block = template_dataset[0:11]

extended_data = []

total_iterations = 0
for i in range(11, len(template_dataset), 11):
    #Se guarda el bloque con las variaciones de la entrada correspondiente a la iteración
    variation_block = template_dataset[i:i+11]

    # Se busca la entrada neutral del bloque, la única que debería tener respuesta
    neutral_response = next((e for e in variation_block if e["Nivel de emoción"] == "0 (Neutral)" and e.get("Respuesta")), None)
    
    # Si no hay respuesta en la emoción neutral, saltamos la generación de este bloque de variaciones (no habrá base con la que generarlas)
    if not neutral_response:
        continue

    for variation in variation_block:
        if not variation.get("Respuesta"):
            # print(f"\n\n********************** VARIACION **********************\n\n{variation}")
            generation_prompt = [
                f"""A continuación adjunto la entrada de un archivo con el que se pretende que un modelo de lenguaje actúe como un personaje:

                {json.dumps(neutral_response, ensure_ascii=False, indent=2)}

                Has de generar una variación de esta respuesta siguiendo la tarea y el nivel emocional reflejados en el prompt siguiente:

                {json.dumps(variation, ensure_ascii=False, indent=2)}

                Para que entiendas mejor cómo generar la respuesta indicada, adjunto un bloque de respuestas de ejemplo con todas las variaciones emocionales con su respuesta:

                {variation_example_block}

                Genera únicamente la respuesta del personaje.
                """
            ]
            try:       
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=generation_prompt,
                    temperature=0.8,
                    max_tokens=200
                )

                print(f"Generando respuesta para entrada {i + variation_block.index(variation)}...")

                print(f"\n\n********************** VARIACION **********************\n\n{variation}")
                variation["Respuesta"] = response.choices[0].message.content.strip()

                print(variation)
                extended_data.append(variation)
                print(f"\n\n********************** FIN VARIACION **********************\n")

            except Exception as e:
                print(f"Error al generar la respuesta: {e}")

print(f"\n\nGeneración de respuestas completa: {total_iterations}")

output_path = os.path.join(BASE_DIR, f"../assets/character_sheets/finetuning_{char_name}_extended.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(extended_data, f, ensure_ascii=False, indent=2)