import os
import json
from datasets import Dataset
from transformers import Trainer, TrainingArguments, DataCollatorForLanguageModeling
from transformers import GPTNeoForCausalLM, GPT2Tokenizer, TextDataset

# Define model and tokenizer
model_name = "EleutherAI/gpt-neo-125M"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPTNeoForCausalLM.from_pretrained(model_name)
# Get current script directory
script_dir = os.path.dirname(__file__)  # This assumes your script is in the same directory as the datasets

# Relative path to datasets
file_path = os.path.join(script_dir, "combined_dataset.json")

with open(file_path, "r", encoding="utf-8") as f:
    dataset = json.load(f)

# Define the TextDataset instance
text_dataset = TextDataset(
    tokenizer=tokenizer,
    file_path=file_path,
    block_size=128,
    overwrite_cache=False,  # Set this to True if you want to overwrite the cache
    cache_dir=None  # You can specify a directory for caching if needed
)

# Data collator for language modeling
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# Training arguments
training_args = TrainingArguments(
    output_dir="./gpt_neo_multitask_finetuned",
    overwrite_output_dir=True,
    num_train_epochs=10,
    per_device_train_batch_size=4,
    save_steps=10_000,
    save_total_limit=2,
)

# Trainer for multi-task learning
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=text_dataset,
)

# Fine-tuning the model for multi-task learning
trainer.train()

# Save the fine-tuned model
model.save_pretrained("./gpt_neo_multitask_finetuned")
tokenizer.save_pretrained("./gpt_neo_multitask_finetuned")
