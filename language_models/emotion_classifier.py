from transformers import AutoModelForSequenceClassification, AutoTokenizer
import os, time, torch
import torch.nn.functional as F  # Importamos para aplicar softmax

# Obtener la ruta absoluta del directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas locales del modelo y el tokenizador
model_path = os.path.join(BASE_DIR, "model/lxyuan_distilbert-base-multilingual-cased-sentiments-student")
tokenizer_path = os.path.join(BASE_DIR, "tokenizer/lxyuan_distilbert-base-multilingual-cased-sentiments-student")

# Cargar el modelo y el tokenizador
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

# Etiquetas de emoción (según la documentación del modelo)
labels = ["Positivo", "Neutral", "Negativo"]

# Introducir entrada de texto: 
text = input("Ingresa un texto que analizar: ").strip()

# Texto base
#text = "Holy Mother of God, what is that??"

# Tokenizar el texto
inputs = tokenizer(text, return_tensors="pt")

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