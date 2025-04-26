import model_manager as model
import socket
import json

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

        # Se genera la respuesta
        result = model.generate_response(model_name, text)
    
    # Se devuelve codigo de error
    except Exception as e:
        result = {"error": str(e)}

    # Se devuelve la respuestas
    client_socket.send(json.dumps(result).encode())
    client_socket.close()