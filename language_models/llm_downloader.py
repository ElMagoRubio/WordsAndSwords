from huggingface_hub import login
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    AutoModelForQuestionAnswering, 
    AutoModelForCausalLM, 
    AutoModelForSeq2SeqLM
)

model_list = [
    ("michellejieli/emotion_text_classifier", AutoModelForSequenceClassification), 
    ("deepset/tinyroberta-squad2", AutoModelForQuestionAnswering),
    ("microsoft/Phi-3.5-mini-instruct", AutoModelForCausalLM),
    ("google/flan-t5-base", AutoModelForSeq2SeqLM)
]

for model_name, ModelClass in model_list:
    print(f"Descargando y guardando el modelo: {model_name}")

    #Reemplazando "/" por "_" para evitar problemas con los nombres de los archivos
    safe_model_name = model_name.replace("/", "_")

    #Descarga y guardado del tokenizador
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.save_pretrained("./tokenizer/" + safe_model_name)
    
    #Descarga y guardado del modelo con su tipo específico
    model = ModelClass.from_pretrained(model_name)
    model.save_pretrained(f"./model/{safe_model_name}")

    print(f"Modelo {model_name} guardado en './model/{safe_model_name}' y su tokenizador en './tokenizer/{safe_model_name}'\n")