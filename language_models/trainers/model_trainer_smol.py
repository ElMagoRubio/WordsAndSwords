from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    TrainingArguments, Trainer, DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from datasets import load_dataset
import gc, os, threading, time
import torch

model_name = "HuggingFaceTB_SmolLM2-360M-Instruct"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas absolutas
tokenizer_path = os.path.abspath(os.path.join(BASE_DIR, f"../tokenizer/{model_name}"))
model_path = os.path.abspath(os.path.join(BASE_DIR, f"../model/{model_name}"))
dataset_path = os.path.abspath(os.path.join(BASE_DIR, "../datasets/finetuning_ready_dataset_1_smol.jsonl"))

# Cargar tokenizer y modelo causal
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")
model = prepare_model_for_kbit_training(model)

# Configuración LoRA para causal LM
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

model = get_peft_model(model, lora_config)

# Cargar dataset
dataset = load_dataset("json", data_files={"train": dataset_path})["train"]
split_dataset = dataset.train_test_split(test_size=0.1, seed=42)
train_dataset = split_dataset["train"]
eval_dataset = split_dataset["test"]

# Preprocesamiento: texto ya contiene el input completo

def preprocess(example):
    tokenized = tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=512
    )
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

tokenized_train = train_dataset.map(preprocess).remove_columns(["text"])
tokenized_eval = eval_dataset.map(preprocess).remove_columns(["text"])

# Argumentos de entrenamiento
args = TrainingArguments(
    output_dir=os.path.abspath(os.path.join(BASE_DIR, "../model/HuggingFaceTB_SmolLM2-360M-Instruct-lora")),
    per_device_train_batch_size=1,
    gradient_accumulation_steps=48,
    num_train_epochs=500,
    eval_strategy="steps",
    eval_steps=10,
    save_strategy="epoch",
    save_total_limit=1,
    logging_steps=1,
    fp16=torch.cuda.is_available(),
    remove_unused_columns=False,
    report_to="none",
    label_names=["labels"]
)

# Trainer
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_eval,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

# Mostrar tiempo

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
model.save_pretrained(os.path.abspath(os.path.join(BASE_DIR, "../model/HuggingFaceTB_SmolLM2-360M-Instruct-lora")))
tokenizer.save_pretrained(os.path.abspath(os.path.join(BASE_DIR, "../tokenizer/HuggingFaceTB_SmolLM2-360M-Instruct-lora")))
