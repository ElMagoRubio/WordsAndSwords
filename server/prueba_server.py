import socket
import sys
import json
import model_manager as model

# Dirección del servidor
HOST = "127.0.0.1"
PORT = 5005

MODELOS = [
    "google_flan-t5-large",
    "HuggingFaceTB_SmolLM2-360M-Instruct",
    "microsoft_Phi-4-mini-instruct"
]

# Texto de ejemplo para las pruebas
TEXTO_EJEMPLO = "Hola, ¿cómo estás hoy? Estoy un poco nervioso por el examen."

print(f"\nArgumentos: {sys.argv}")
i = 0
for a in sys.argv:
    print(f"Argumento {i}: {a}")
    i += 1

if (len(sys.argv) == 2):
    model_name = MODELOS[int(sys.argv[1])]
    print(f"\nSólo un argumento, pasando prompt de ejemplo al modelo {model_name}.")
    text = TEXTO_EJEMPLO


elif (len(sys.argv) == 3):
    model_name = MODELOS[int(sys.argv[1])]
    print(f"\nPasando prompt al modelo {model_name}.")
    text = sys.argv[2]

else:
    print(f"\nERROR: Número de argumentos incorrecto. Ejecutar como: './prueba_server.py numero_modelo prompt_entrada'")
    exit(1)

print(f"\nProbando generate_response con modelo: {model_name}")
try:
    # Crear socket de cliente
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # Crear petición
    request = {
        "model": model_name,
        "text": text
    }

    print(f"\nRequest: {request}")
    
    print(f"\nEnviando petición...")
    client_socket.send(json.dumps(request).encode())

    # Recibir respuesta
    response = client_socket.recv(4096).decode()
    client_socket.close()

    result = json.loads(response)
    print(f"Respuesta del modelo: {result}")
except Exception as e:
    print("Error:", e)