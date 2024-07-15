import json
from transformers import GPT2Tokenizer

# Load the tokenizer
model_name = "EleutherAI/gpt-neo-125M"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Path to your JSON dataset file
json_file = "person_dataset.json"

# Function to calculate average and maximum token count
def calculate_token_counts(json_file, tokenizer):
    with open(json_file, "r", encoding="utf-8") as file:
        dataset = json.load(file)
    
    total_tokens = 0
    total_examples = len(dataset)
    max_token_count = 0
    
    for example in dataset:
        # Convert JSON object to text
        text = json.dumps(example, ensure_ascii=False)
        
        # Tokenize the text
        tokens = tokenizer.encode(text)
        
        # Count tokens (excluding special tokens like [CLS], [SEP])
        token_count = len(tokens) - 2  # subtracting 2 for [CLS] and [SEP]
        
        total_tokens += token_count
        
        # Update maximum token count if current example has more tokens
        if token_count > max_token_count:
            max_token_count = token_count
    
    average_token_count = total_tokens / total_examples
    return max_token_count, average_token_count

# Calculate maximum and average token count
max_token_count, average_token_count = calculate_token_counts(json_file, tokenizer)
print(f"Maximum token count in any JSON object: {max_token_count}")
print(f"Average token count per JSON object: {average_token_count}")

# Set block_size slightly larger than average_token_count
block_size = int(average_token_count) + 10  # Adding a buffer of 10 tokens
print(f"Suggested block_size: {block_size}")
