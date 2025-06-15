from transformers import (
    AutoTokenizer, AutoModelForSeq2SeqLM,
    TrainingArguments, Trainer, DataCollatorForSeq2Seq
)
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from datasets import load_dataset
import gc, os, threading, time
import torch

model_name = "google_flan-t5-large"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas absolutas
tokenizer_path = os.path.abspath(os.path.join(BASE_DIR, f"../tokenizer/{model_name}"))
model_path = os.path.abspath(os.path.join(BASE_DIR, f"../model/{model_name}"))
dataset_path = os.path.abspath(os.path.join(BASE_DIR, "../datasets/finetuning_ready_dataset_1_flant5.jsonl"))

# Cargar tokenizer y modelo
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path, device_map="auto")

# Preparar modelo para LoRA
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q", "v"],
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.SEQ_2_SEQ_LM
)

model = get_peft_model(model, lora_config)

# Cargar y dividir dataset
dataset = load_dataset("json", data_files={"train": dataset_path})["train"]
split_dataset = dataset.train_test_split(test_size=0.1, seed=42)
train_dataset = split_dataset["train"]
eval_dataset = split_dataset["test"]

# Preprocesamiento
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

tokenized_train = train_dataset.map(preprocess).remove_columns(["input", "target"])
tokenized_eval = eval_dataset.map(preprocess).remove_columns(["input", "target"])

# Argumentos de entrenamiento con correcciones
args = TrainingArguments(
    output_dir=os.path.abspath(os.path.join(BASE_DIR, "../model/flan-t5-lora")),
    per_device_train_batch_size=1,
    gradient_accumulation_steps=48,
    num_train_epochs=250,
    eval_strategy="steps",  
    eval_steps=10,
    save_strategy="epoch",
    save_total_limit=1,
    logging_steps=1,
    fp16=torch.cuda.is_available(),
    remove_unused_columns=False,
    report_to="none",
    label_names=["labels"],  
)

# Trainer (sin el parámetro 'tokenizer')
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_eval,
    data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
)

# Mostrar tiempo cada 10 segundos
def mostrar_tiempo_entrenamiento():
    inicio = time.time()
    while not entrenamiento_finalizado:
        tiempo = int(time.time() - inicio)
        print(f"***** [Tiempo transcurrido]: {tiempo // 60} min {tiempo % 60} seg *****")
        time.sleep(10)

entrenamiento_finalizado = False
contador_thread = threading.Thread(target=mostrar_tiempo_entrenamiento)
contador_thread.start()

gc.collect()
torch.cuda.empty_cache()

# Entrenar
trainer.train()

entrenamiento_finalizado = True
contador_thread.join()

# Guardar modelo LoRA y tokenizer
model.save_pretrained(os.path.abspath(os.path.join(BASE_DIR, "../model/flan-t5-lora")))
tokenizer.save_pretrained(os.path.abspath(os.path.join(BASE_DIR, "../tokenizer/flan-t5-lora")))
