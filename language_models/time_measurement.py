import os, re, sys, subprocess

# Obtener la ruta absoluta del directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Diccionario de scripts disponibles
scripts = {
    "1": os.path.join(BASE_DIR, "emotion_classifier.py"),
    "2": os.path.join(BASE_DIR, "text_generation_flant5.py"),
    "3": os.path.join(BASE_DIR, "text_generation_phi.py"),
    "4": os.path.join(BASE_DIR, "text_generation_tinyroberta.py")
}

# Verificar que se han pasado los argumentos necesarios
if len(sys.argv) != 3:
    print("Uso: python script.py <opción (1-4)> <número de ejecuciones>")
    sys.exit(1)

opcion = sys.argv[1]
num_ejecuciones = sys.argv[2]

# Validar opción de script
if opcion not in scripts:
    print("Error: La opción debe ser un número entre 1 y 4.")
    sys.exit(1)

# Validar número de ejecuciones
try:
    num_ejecuciones = int(num_ejecuciones)
    if num_ejecuciones <= 0:
        raise ValueError
except ValueError:
    print("Error: El número de ejecuciones debe ser un entero positivo.")
    sys.exit(1)

script_a_ejecutar = scripts[opcion]
tiempos = []

print(f"Ejecutando {script_a_ejecutar} {num_ejecuciones} veces...")

# Ejecutar el script seleccionado varias veces
for _ in range(num_ejecuciones):
    resultado = subprocess.run(["python", script_a_ejecutar], capture_output=True, text=True)

    # Buscar el tiempo de respuesta en la salida del script
    match = re.search(r"Tiempo de respuesta:\s*([\d.]+)\s*s", resultado.stdout)
    if match:
        tiempo = float(match.group(1))
        tiempos.append(tiempo)

# Calcular y mostrar la media de los tiempos
if tiempos:
    tiempo_medio = sum(tiempos) / len(tiempos)
    print(f"Tiempo medio de respuesta: {tiempo_medio:.4f} s")
else:
    print("No se pudo obtener el tiempo de respuesta de las ejecuciones.")
