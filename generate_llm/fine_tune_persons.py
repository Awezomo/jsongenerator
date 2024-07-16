import os
import json
from transformers import GPTNeoForCausalLM, GPT2Tokenizer, TextDataset, DataCollatorForLanguageModeling, Trainer, TrainingArguments

# Load the pre-trained GPT-Neo model
model_name = "EleutherAI/gpt-neo-125M"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPTNeoForCausalLM.from_pretrained(model_name)

# Set padding token
tokenizer.pad_token = tokenizer.eos_token

# Load your dataset from the JSON file
with open("person_dataset.json", "r", encoding="utf-8") as file:
    dataset = json.load(file)

# Define the TextDataset instance
text_dataset = TextDataset(
    tokenizer=tokenizer,
    file_path="person_dataset.json",
    block_size=128,
    overwrite_cache=False,  # Set this to True if you want to overwrite the cache
    cache_dir=None  # You can specify a directory for caching if needed
)

# Data collator for language modeling
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# Training arguments
training_args = TrainingArguments(
    output_dir="./gpt_neo_finetuned",
    overwrite_output_dir=True,
    num_train_epochs=10,
    per_device_train_batch_size=4,
    save_steps=10_000,
    save_total_limit=2,
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=text_dataset,
)

# Fine-tuning the model
trainer.train()

# Save the fine-tuned model
model.save_pretrained("./gpt_neo_finetuned")
tokenizer.save_pretrained("./gpt_neo_finetuned")
