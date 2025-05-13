import model_manager as model
import json, os, socket, sys

# Se validan los argumentos
if (len(sys.argv) != 2):
    raise ValueError(f"ERROR: Número de argumentos incorrecto.\nFormato: (./server.py) (nombre_personaje)")

char_name = sys.argv[1]

#Se carga la lista de personajes
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
char_list = model.load_json(os.path.join(BASE_DIR, "../assets/character_sheets/character_list.json"))
task_descriptions = model.load_json(os.path.join(BASE_DIR, "../assets/character_sheets/prompts.json"))
# print(f"\n\nTareas asignadas al modelo: \n{task_descriptions["DEFAULT_PROMPT"]}\n\n{task_descriptions["INTERACTION_LIMIT_PROMPT"]}\n\n{task_descriptions["EMOTION_UPPER_THRESHOLD"]}\n\n{task_descriptions["EMOTION_LOWER_THRESHOLD"]}")

#Validación de nombre de personaje
normalized_char_name = model.normalize_text(char_name)
if normalized_char_name not in char_list:
    raise ValueError(f"ERROR: Personaje '{sys.argv}' no encontrado en character_list.json.")

print(f"\n\nCargando archivos del personaje {char_name}")

#Se cargan los archivos de contexto
token_list = model.load_json(os.path.join(BASE_DIR, f"../assets/character_sheets/lista_tokens_{normalized_char_name}.json"))
print(f"\nCargado archivo de lista de tokens para {char_name}")
context_dict = model.load_json(os.path.join(BASE_DIR, f"../assets/character_sheets/ficha_pj_{normalized_char_name}.json"))
print(f"\nCargado archivo de contexto.")

char_description = context_dict[char_name]

# print(f"\n\nDescripción del personaje: {char_description}")

# Declaración de constantes de control (número máximo de interacciones, umbral emocional maximo y minimo)
MAX_DIALOGUE_INTERACTION = 15
POSITIVE_EMOTION_THRESHOLD = 5
NEGATIVE_EMOTION_THRESHOLD = -5


# Declaración de variables persistentes entre bucles
interaction_count = 0
emotion_level = 0
context_tokens = []
history = []
action = "dialogar"

# Se declara la IP y el puerto
HOST = "127.0.0.1"
PORT = 5005


# Se cargan los modelos
print("Iniciando servidor y cargando modelos...")
model.load_models()


# Se inicia el servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

# Se envía una señal de confirmación de carga a Godot
with open(os.path.join(BASE_DIR, "server_ready.flag"), "w") as f:
    f.write("READY")

print(f"Servidor en ejecución en {HOST}:{PORT}")

# Bucle del servidor
while interaction_count < MAX_DIALOGUE_INTERACTION:
    # Abrimos el puerto y escuchamos los datos
    client_socket, addr = server_socket.accept()
    data = client_socket.recv(1024).decode()

    #Mientras no haya errores
    try:
        # Se aumenta el contador de interacciones
        interaction_count += 1

        # Se convierte texto a diccionario de python
        request = json.loads(data)

        #Se extraen modelo y texto
        model_name = request["model"]
        text = request["text"]

        if text == "CLOSE_SERVER" and model_name == "--":
            print("\n\nSolicitud de cierre recibida. Cerrando servidor...")
            client_socket.send(json.dumps({"response": "Servidor cerrado."}).encode())
            client_socket.close()
            break


        print(f"\nNombre del modelo: {model_name}")
        print(f"\nTexto: {text}")
        print(f"PJ: {char_name}")

        emotion = model.detect_emotion(text)        
        # print(f"\nTexto + emocion detectada: {emotion}")


        if emotion == "negativa":
            emotion_level -= 1
        elif emotion == "positiva":
            emotion_level += 1


        if emotion_level >= POSITIVE_EMOTION_THRESHOLD:
            print("\n\nUmbral de emoción positiva alcanzado.")
            task_description = task_descriptions["EMOTION_UPPER_THRESHOLD"]
            action = "rendirse"

        elif emotion_level <= NEGATIVE_EMOTION_THRESHOLD:
            print("\n\nUmbral de emoción negativa alcanzado.")
            task_description = task_descriptions["EMOTION_LOWER_THRESHOLD"]
            action = "retar"
        
        elif interaction_count >= MAX_DIALOGUE_INTERACTION:
            print("\n\nLímite de interacciones máximas alcanzadas.")
            task_description = task_descriptions["INTERACTION_LIMIT_PROMPT"]
            action = "retar"
        
        else:            
            # Descripción de la tarea que ha de realizar modelo
            task_description = task_descriptions["DEFAULT_PROMPT"]
        

        context_tokens = model.add_context(text, context_tokens, token_list, context_dict)
        # print(f"\n\nTokens de contexto: {context_tokens}")

        prompt = model.build_prompt(text, task_description, emotion, char_name, char_description, context_tokens, context_dict, history, model_name)
        
        # Se genera la respuesta
        response = model.generate_response(model_name, prompt)

        # Sanea la respuesta para Smol, que devuelve también el prompt de entrada
        if model_name == "HuggingFaceTB_SmolLM2-360M-Instruct":
            response = model.process_response(result, char_name)        
        
        print(f"\n\nRespuesta: {response}")

        result = {
            "response": f"{response}",
            "emotion_level": f"{emotion_level}",
            "action": f"{action}"
        }

        # Guardar conversación para siguiente iteración
        if (action == "dialogar"):
            history.append((text, response))
        # print(f"\n\nHistorial: {history}")
    
    # Se devuelve codigo de error
    except Exception as e:
        result = {"error": str(e)}

    # Se devuelve la respuestas
    client_socket.send(json.dumps(result).encode())
    client_socket.close()

# Se cierra el server
if os.path.exists(os.path.join(BASE_DIR, "server_ready.flag")):
    os.remove(os.path.join(BASE_DIR, "server_ready.flag"))

server_socket.close()