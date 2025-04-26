from llm_loader import get_model_and_tokenizer_from_index
import sys, time, torch
import torch.nn.functional as F  # Importamos para aplicar softmax

if (len(sys.argv) != 2):
    print("ERROR: Número de argumentos incorrecto.\nFormato: (./emotion_classifier.py) (texto_entrada_usuario)")
    exit(1)

# Detectar si hay GPU disponible
device = "cuda" if torch.cuda.is_available() else "cpu"

# Cargar modelo y tokenizador
tokenizer, model = get_model_and_tokenizer_from_index(0)

# Etiquetas de emoción (según la documentación del modelo)
labels = ["Positivo", "Neutral", "Negativo"]

# Introducir entrada de texto: 
text = sys.argv[1].strip()

# Texto base
#text = "Holy Mother of God, what is that??"

# Tokenizar el texto
inputs = tokenizer(text, return_tensors="pt").to(device)

# Inicio de medición del tiempo de generación de respuesta
start_time = time.time()

# Obtener las predicciones
with torch.no_grad():
    outputs = model(**inputs)

# Obtener las logits y aplicar softmax para obtener probabilidades
logits = outputs.logits
probabilities = F.softmax(logits, dim=1).squeeze().tolist()

#Calcular el tiempo de respuesta
total_time = time.time() - start_time

# Mostrar todas las probabilidades
print(f"Texto: {text}")
for label, prob in zip(labels, probabilities):
    print(f"{label}: {prob:.4f}")

# Obtener la emoción con mayor probabilidad
predicted_class = torch.argmax(logits, dim=1).item()
predicted_emotion = labels[predicted_class]

#Mostrar la respuesta y el tiempo de respuesta
print(f"Emoción predicha: {predicted_emotion}\n")
print(f"Tiempo de respuesta: {total_time:.4f} segundos")