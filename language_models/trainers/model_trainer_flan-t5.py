from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, TrainingArguments, Trainer, DataCollatorForSeq2Seq
from datasets import load_dataset
import gc, os, threading, time 

# Optimización de la gestión de memoria de PyTorch
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
import torch

model_name = "google_flan-t5-large"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas
dataset_path = os.path.join(BASE_DIR, "../finetuning_ready_dataset_1_flant5.jsonl")
tokenizer_path = os.path.join(BASE_DIR, f"../tokenizer/{model_name}")
model_path = os.path.join(BASE_DIR, f"../model/{model_name}")

# Cargar tokenizer y modelo desde disco
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

# Cargar dataset
dataset = load_dataset("json", data_files={"train": dataset_path})["train"]

# Función de preprocesamiento
def preprocess(example):
    model_input = tokenizer(
        example["input"],
        max_length=512,
        truncation=True,
        padding="max_length"
    )
    target = tokenizer(
        text_target=example["target"],
        max_length=128,
        truncation=True,
        padding="max_length"
    )
    model_input["labels"] = target["input_ids"]

    return {
        "input_ids": model_input["input_ids"],
        "attention_mask": model_input["attention_mask"],
        "labels": model_input["labels"]
    }

# Aplicar preprocesamiento al dataset
tokenized_dataset = dataset.map(preprocess, batched=False)
tokenized_dataset = tokenized_dataset.remove_columns(["input", "target"])

# Configurar entrenamiento
args = TrainingArguments(
    output_dir=os.path.join(BASE_DIR, "../model/flan-t5-finetuned_v1"),
    per_device_train_batch_size=1,
    gradient_accumulation_steps=48,         # simula un batch_size de 48
    num_train_epochs=5,
    logging_steps=10,
    save_strategy="epoch",
    save_total_limit=1,
    fp16=torch.cuda.is_available(),
    remove_unused_columns=False,
    report_to="none"
)

# Crear trainer
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
    data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
)

# Función que imprime el tiempo de entrenamiento cada 30 segundos, comprobación de que está ejecutando
def mostrar_tiempo_entrenamiento():
    inicio = time.time()
    while not entrenamiento_finalizado:
        tiempo = int(time.time() - inicio)
        print(f"********************************** [Tiempo transcurrido]: {tiempo // 60} min {tiempo % 60} seg **********************************")
        time.sleep(10)

entrenamiento_finalizado = False
contador_thread = threading.Thread(target=mostrar_tiempo_entrenamiento)
contador_thread.start()

# Liberamos memoria antes del entrenamiento
gc.collect()
torch.cuda.empty_cache()

# Entrenamiento
trainer.train()

# Finalizar el temporizador
entrenamiento_finalizado = True
contador_thread.join()

# Guardar modelo
trainer.save_model(os.path.join(BASE_DIR, "../model/flan-t5-finetuned_v1"))
tokenizer.save_pretrained(os.path.join(BASE_DIR, "../tokenizer/flan-t5-finetuned_v1"))
