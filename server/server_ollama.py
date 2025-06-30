import model_manager as model
import json, os, socket, sys, time

DEBUG_MODE = True

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
if normalized_char_name in char_list:
    #Descripción del personaje
    char_description = char_list[normalized_char_name]
    if (DEBUG_MODE):
        print(f"\n\n[{char_name}]: {char_description}")
else:
    raise ValueError(f"ERROR: Personaje '{sys.argv}' no encontrado en character_list.json.")

print(f"\n\nCargando archivos del personaje {char_name}")

#Se cargan los archivos de contexto
token_list = model.load_json(os.path.join(BASE_DIR, f"../assets/character_sheets/lista_tokens_{normalized_char_name}.json"))
print(f"\nCargado archivo de lista de tokens para {char_name}")
context_dict = model.load_json(os.path.join(BASE_DIR, f"../assets/character_sheets/ficha_pj_{normalized_char_name}.json"))
print(f"\nCargado archivo de contexto.")


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
print("Iniciando servidor...")


# Se inicia el servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

# Se envía una señal de confirmación de carga a Godot
with open(os.path.join(BASE_DIR, "server_ready.flag"), "w") as f:
    f.write("READY")

print(f"Servidor en ejecución en {HOST}:{PORT}")


# Abrimos el puerto y escuchamos los datos

client_socket = None

# Bucle del servidor
while interaction_count < MAX_DIALOGUE_INTERACTION and action == 'dialogar':
    if client_socket == None:
        try:
            client_socket, addr = server_socket.accept()
            if (DEBUG_MODE):
                print(f"Cliente conectado en el socket {client_socket} con dirección {addr}")
        
        except Exception as e:
            if (DEBUG_MODE):
                print(f"[ERROR] Aceptando cliente: {e}")
            continue

    #Mientras no haya errores
    try:
        data = client_socket.recv(1024).decode()

        if not data:
            if (DEBUG_MODE):
                print("[INFO] Cliente desconectado.")
            client_socket.close()
            client_socket = None
            break

        request = json.loads(data)

        request_code = request["code"]

        if (request_code == "PING"):
            if (DEBUG_MODE):
                print("\n\nPONG")
            result = "PONG"
        
        elif (request_code == "GENERATE"):
            if (DEBUG_MODE):
                print("\n\nGENERANDO RESPUESTA...")

            interaction_count += 1

            model_name = request["model"]
            text = request["text"]

            if (DEBUG_MODE):
                print(f"\n\nNombre del modelo: {model_name}")
                print(f"\nTexto: {text}")
                print(f"\nPJ: {char_name}")

            emotion = model.detect_emotion(text)

            if (DEBUG_MODE):
                print(f"\n\nEmoción detectada: {emotion}")

            if emotion == "negativa":
                if emotion_level > -5:
                    emotion_level -= 1
            elif emotion == "positiva":
                if emotion_level < 5:
                    emotion_level += 1

            if (DEBUG_MODE):
                print(f"\n\nNivel de emoción: {emotion_level}")

            if emotion_level >= POSITIVE_EMOTION_THRESHOLD:
                if (DEBUG_MODE):
                    print("\n\nUmbral de emoción positiva alcanzado.")
                task_description = task_descriptions["EMOTION_UPPER_THRESHOLD"]
                action = "rendirse"

            elif emotion_level <= NEGATIVE_EMOTION_THRESHOLD:
                if (DEBUG_MODE):
                    print("\n\nUmbral de emoción negativa alcanzado.")
                task_description = task_descriptions["EMOTION_LOWER_THRESHOLD"]
                action = "retar"
            
            elif interaction_count >= MAX_DIALOGUE_INTERACTION:
                if (DEBUG_MODE):
                    print("\n\nLímite de interacciones máximas alcanzadas.")
                task_description = task_descriptions["INTERACTION_LIMIT_PROMPT"]
                action = "retar"
            
            else:            
                # Descripción de la tarea que ha de realizar modelo
                task_description = task_descriptions["DEFAULT_PROMPT"]
            
            if (DEBUG_MODE):
                print(f"\n\nDescripción de la tarea:\n{task_description}")
            
            context_tokens = model.add_context(text, context_tokens, token_list, context_dict)
            if (DEBUG_MODE):
                print(f"\n\nTokens de contexto:\n{context_tokens}")

            prompt = model.build_prompt(text, task_description, emotion_level, char_name, char_description, context_tokens, context_dict, history, model_name, DEBUG_MODE)
            if (DEBUG_MODE):
                print(f"\n\nPrompt generado:\n{prompt}")
            
            # Se genera la respuesta
            response = model.generate_response_with_ollama(prompt, model_name)
            if (DEBUG_MODE):
                print(f"\n\nRespuesta generada:\n{response}")

            response = model.process_response(response, char_name)

            if(DEBUG_MODE):
                print(f"\n\nRespuesta procesada:\n{response}")

            # Guardar conversación para siguiente iteración
            if (action == "dialogar"):
                history.append((text, response))                
                if (DEBUG_MODE):
                    print(f"\n\nHistorial: {history}")

            result = {
                "response": f"{response}",
                "emotion_level": f"{emotion_level}",
                "action": f"{action}"
            }

        elif (request_code == "CLOSE"):
            if (DEBUG_MODE):
                print("\n\nCERRANDO SERVER")
            break

    except (ConnectionResetError, BrokenPipeError):
        if DEBUG_MODE:
            print("[INFO] Cliente desconectado inesperadamente.")
        client_socket = None 
        
        continue
            
    except Exception as e:
        result = {"error": str(e)}
        continue
    
    # Se devuelve la respuestas
    client_socket.send(json.dumps(result).encode('utf-8'))


time.sleep(1)

if client_socket:
    client_socket.send(json.dumps("SERVIDOR CERRADO").encode())
    client_socket.close()

if os.path.exists(os.path.join(BASE_DIR, "server_ready.flag")):
    os.remove(os.path.join(BASE_DIR, "server_ready.flag"))

server_socket.close()

if(DEBUG_MODE):
    print("SERVIDOR CERRADO")