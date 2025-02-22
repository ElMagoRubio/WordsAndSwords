from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# Ruta local donde descargaste el modelo
model_path = "./model/michellejieli_emotion_text_classifier"
tokenizer_path = "./tokenizer/michellejieli_emotion_text_classifier"

# Cargar el modelo y el tokenizador
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

# Texto a analizar
texts = [
    "What the hell is that?",
    "I cried for hours.",
    "Hello there.",
    "Yay!",
    "Please, don't kill me!",
    "You disgust me.",
    "I'm gonna murder you."
]

for text in texts:
    # Tokenizar el texto
    inputs = tokenizer(text, return_tensors="pt")

    # Pasar por el modelo para obtener las predicciones
    with torch.no_grad():
        outputs = model(**inputs)

    # Obtener la emoción predicha
    logits = outputs.logits
    predicted_class = torch.argmax(logits, dim=1).item()

    # Etiquetas de emoción (según la documentación del modelo)
    labels = ["anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"]
    predicted_emotion = labels[predicted_class]

    # Mostrar resultado
    print(f"Texto: {text}")
    print(f"Emoción predicha: {predicted_emotion}\n")
