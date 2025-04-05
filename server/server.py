import model_manager as model
import socket
import json

HOST = "127.0.0.1"
PORT = 5005

print("Iniciando servidor y cargando modelos...")
model.load_models()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Servidor en ejecución en {HOST}:{PORT}")

while True:
    client_socket, addr = server_socket.accept()
    data = client_socket.recv(1024).decode()

    try:
        request = json.loads(data)
        model_name = request["model"]
        text = request["text"]
        result = model.generate_response(model_name, text)
    except Exception as e:
        result = {"error": str(e)}

    client_socket.send(json.dumps(result).encode())
    client_socket.close()