import model_manager as model
import json, os, socket, sys

# Se validan los argumentos
if (len(sys.argv) != 2):
    raise ValueError(f"ERROR: Número de argumentos incorrecto.\nFormato: (./server.py) (nombre_personaje)")

char_name = sys.argv[1]

#Se carga la lista de personajes
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
char_list = model.load_json(os.path.join(BASE_DIR, "../assets/character_sheets/character_list.json"))


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

print(f"\n\nDescripción del personaje: {char_description}")

# Historial de conversación del personaje
context_tokens = []
history = []

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

print(f"Servidor en ejecución en {HOST}:{PORT}")

# Bucle del servidor
while True:
    # Abrimos el puerto y escuchamos los datos
    client_socket, addr = server_socket.accept()
    data = client_socket.recv(1024).decode()

    #Mientras no haya errores
    try:
        # Se convierte texto a diccionario de python
        request = json.loads(data)

        #Se extraen modelo y texto
        model_name = request["model"]
        text = request["text"]

        # Descripción de la tarea que ha de realizar modelo
        if (model_name == "google_flan-t5-large"):
            task_description = f"\nImita al personaje como si estuvieras interpretando su papel en una obra de teatro. Sé coherente con su personalidad y conocimientos. Genera una única respuesta autocontenida. El límite es de 4 frases."
        elif (model_name == "HuggingFaceTB_SmolLM2-360M-Instruct"):
            task_description = f"\nSimula al personaje de forma coherente con su personalidad y conocimientos. Genera una única respuesta autocontenida. El límite es de 4 frases. No generes conversación adicional."


        print(f"\nNombre del modelo: {model_name}")
        print(f"\nTexto: {text}")
        print(f"PJ: {char_name}")

        emotion = model.detect_emotion(text)

        # print(f"\nTexto + emocion detectada: {emotion}")

        context_tokens = model.add_context(text, context_tokens, token_list, context_dict)
        # print(f"\n\nTokens de contexto: {context_tokens}")

        prompt = model.build_prompt(text, task_description, emotion, char_name, char_description, context_tokens, context_dict, history, model_name)
        
        # Se genera la respuesta
        result = model.generate_response(model_name, prompt)

        # Sanea la respuesta para Smol, que devuelve también el prompt de entrada
        if model_name == "HuggingFaceTB_SmolLM2-360M-Instruct":
            result = model.process_response(result, char_name)        
        
        print(f"\n\nRespuesta: {result}")

        # Guardar conversación para siguiente iteración
        history.append((text, result))
        # print(f"\n\nHistorial: {history}")
    
    # Se devuelve codigo de error
    except Exception as e:
        result = {"error": str(e)}

    # Se devuelve la respuestas
    client_socket.send(json.dumps(result).encode())
    client_socket.close()