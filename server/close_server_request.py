import json, socket

# Dirección del servidor
HOST = "127.0.0.1"
PORT = 5005

try:
    # Crear socket de cliente
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # Crear petición
    request = {
        "code": "CLOSE_SERVER"
    }

    client_socket.send(json.dumps(request).encode())

    # Recibir respuesta
    response = client_socket.recv(4096).decode()
    client_socket.close()

    result = json.loads(response)

    print(json.dumps(result))

except Exception as e:
    print(json.dumps({
    "response": "Error de cierre de servidor"
}))