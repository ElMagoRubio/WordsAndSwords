from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import load_dataset
import gc, os, threading, time

# Optimización de la gestión de memoria de PyTorch
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
import torch

model_name = "HuggingFaceTB_SmolLM2-360M-Instruct"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas al dataset y modelo/tokenizador
dataset_path = os.path.join(BASE_DIR, "../finetuning_ready_dataset_1_smol.jsonl")
tokenizer_path = os.path.join(BASE_DIR, f"../tokenizer/{model_name}")
model_path = os.path.join(BASE_DIR, f"../model/{model_name}")

# Cargar tokenizer y modelo desde Hugging Face o ruta local
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

# Cargar dataset JSONL
dataset = load_dataset("json", data_files={"train": dataset_path})["train"]

# Función de preprocesamiento: tokeniza campo "text" completo
def preprocess(example):
    full_text = example["text"]
    tokenized = tokenizer(
        full_text,
        max_length=512,
        truncation=True,
        padding="max_length"
    )
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

# Tokenizar el dataset
tokenized_dataset = dataset.map(preprocess, batched=False)
tokenized_dataset = tokenized_dataset.remove_columns(["text"])

# Argumentos de entrenamiento
args = TrainingArguments(
    output_dir=os.path.join(BASE_DIR, "../model/smol-finetuned-v1"),
    per_device_train_batch_size=2,
    gradient_accumulation_steps=48,
    num_train_epochs=5,
    logging_steps=10,
    save_strategy="epoch",
    save_total_limit=1,
    fp16=torch.cuda.is_available(),
    remove_unused_columns=False,
    report_to="none"
)

# Collator para entrenamiento causal (no MLM)
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

# Crear instancia de Trainer
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# Función auxiliar: muestra tiempo de entrenamiento cada 10 segundos
def mostrar_tiempo_entrenamiento():
    inicio = time.time()
    while not entrenamiento_finalizado:
        tiempo = int(time.time() - inicio)
        print(f"[Tiempo transcurrido]: {tiempo // 60} min {tiempo % 60} seg")
        time.sleep(10)

# Iniciar temporizador en segundo plano
entrenamiento_finalizado = False
contador_thread = threading.Thread(target=mostrar_tiempo_entrenamiento)
contador_thread.start()

# Limpiar memoria antes del entrenamiento
gc.collect()
torch.cuda.empty_cache()

# Ejecutar entrenamiento
trainer.train()

# Finalizar contador de tiempo
entrenamiento_finalizado = True
contador_thread.join()

# Guardar modelo y tokenizer entrenados
trainer.save_model(os.path.join(BASE_DIR, "../model/smol-finetuned-v1"))
tokenizer.save_pretrained(os.path.join(BASE_DIR, "../tokenizer/smol-finetuned-v1"))
