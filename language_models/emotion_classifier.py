from transformers import AutoModelForSequenceClassification, AutoTokenizer
import os, time, torch
import torch.nn.functional as F  # Importamos para aplicar softmax

# Obtener la ruta absoluta del directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas locales del modelo y el tokenizador
model_path = os.path.join(BASE_DIR, "model/michellejieli_emotion_text_classifier")
tokenizer_path = os.path.join(BASE_DIR, "tokenizer/michellejieli_emotion_text_classifier")

# Cargar el modelo y el tokenizador
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

# Texto a analizar
texts = ["Holy Mother of Christ"]

# Etiquetas de emoción (según la documentación del modelo)
labels = ["ira", "asco", "miedo", "alegría", "neutral", "tristeza", "sorpresa"]

for text in texts:
    # Tokenizar el texto
    inputs = tokenizer(text, return_tensors="pt")

    # Pasar por el modelo para obtener las predicciones
    with torch.no_grad():
        outputs = model(**inputs)

    # Obtener las logits y aplicar softmax para obtener probabilidades
    logits = outputs.logits
    probabilities = F.softmax(logits, dim=1).squeeze().tolist()

    # Mostrar todas las probabilidades
    print(f"Texto: {text}")
    for label, prob in zip(labels, probabilities):
        print(f"{label}: {prob:.4f}")
    
    # Obtener la emoción con mayor probabilidad
    predicted_class = torch.argmax(logits, dim=1).item()
    predicted_emotion = labels[predicted_class]

    print(f"Emoción predicha: {predicted_emotion}\n")
