import socket
import sys
import json
import model_manager as model

# Dirección del servidor
HOST = "127.0.0.1"
PORT = 5005
DEBUG_MODE = True

MODELOS = [
    "mistral",
    "mistral",
    "mistral",
    "mistral"
]

# Texto de ejemplo para las pruebas
TEXTO_EJEMPLO = "Texto de ejemplo"

if (DEBUG_MODE):
    print(f"\nArgumentos: {sys.argv}")
i = 0
for a in sys.argv:
    if (DEBUG_MODE):
        print(f"Argumento {i}: {a}")
    i += 1

if (len(sys.argv) == 2):
    code = sys.argv[1]
    model_name = "--"
    text = ""
    if (DEBUG_MODE):
        print(f"\nSólo un argumento, mandando PING o CERRANDO SERVER.")
    

elif (len(sys.argv) == 3):    
    code = sys.argv[1]
    if (code == "GENERATE"):
        model_name = MODELOS[int(sys.argv[2])]
        if (DEBUG_MODE):
            print(f"\nSólo un argumento, pasando prompt de ejemplo al modelo {model_name}.")
        text = TEXTO_EJEMPLO


elif (len(sys.argv) == 4):    
    code = sys.argv[1]
    if (code == "GENERATE"):
        model_name = MODELOS[int(sys.argv[2])]
        if (DEBUG_MODE):
            print(f"\nPasando prompt al modelo {model_name}.")
        text = sys.argv[3]

else:
    print(f"\nERROR: Número de argumentos incorrecto. Ejecutar como: './prueba_server.py codigo (numero_modelo) (prompt_entrada)'")
    exit(1)

if (DEBUG_MODE):
    print(f"\nProbando generate_response con modelo: {model_name}")

try:
    # Crear socket de cliente
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # Crear petición
    request = {
        "code": code,
        "model": model_name,
        "text": text
    }

    if (DEBUG_MODE):
        print(f"\nRequest: {request}")
    
    if (DEBUG_MODE):
        print(f"\nEnviando petición...")
    client_socket.send(json.dumps(request).encode())

    # Recibir respuesta
    response = client_socket.recv(4096).decode()
    client_socket.close()

    result = json.loads(response)

    if (DEBUG_MODE):
        print("Respuesta del servidor: ")

    print(json.dumps(result, ensure_ascii=False))
          
except Exception as e:
    print(json.dumps({
        "response": "Error de conexion",
        "emotion_level": "0",
        "action": "dialogar"
    }))