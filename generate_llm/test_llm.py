import json
import re
import torch
from transformers import GPTNeoForCausalLM, GPT2Tokenizer, set_seed, pipeline

# Load your fine-tuned model and tokenizer
model_name = "./gpt_neo_multitask_finetuned"  # Replace with the path to your fine-tuned model
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPTNeoForCausalLM.from_pretrained(model_name)

# Set the device to GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Set the generator pipeline
generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=device)

def clean_and_combine_tokens(tokens):
    """Clean tokens by removing special characters and combining fragmented words."""
    cleaned_tokens = []
    i = 0
    while i < len(tokens):
        token = tokens[i].replace('Ġ', ' ').replace('Ċ', '\n').strip('" ,')
        if token:
            # Check if the next token should be combined
            if (i + 1) < len(tokens) and tokens[i + 1] not in ['"', ' ', ',', ':', '{', '}', '[', ']']:
                token += tokens[i + 1].replace('Ġ', '').replace('Ċ', '').strip('" ,')
                i += 1
            cleaned_tokens.append(token)
        i += 1
    return cleaned_tokens

def extract_key_value_pairs(text):
    """
    Extract key-value pairs from the text and return a dictionary.
    """
    lines = text.split('\n')
    data = {}
    keys = {
        "title", "description", "startdate", "enddate",
        "geoinfo", "duration", "purpose", "role", "rank",
        "phase", "unit", "level", "tasktype", "bereich"
    }
    geoinfo_keys = {"name", "latitude", "longitude"}

    current_key = None
    current_dict = None

    for line in lines:
        line = line.strip()
        if ':' in line:
            key_value = line.split(':', 1)
            if len(key_value) == 2:
                key, value = key_value
                key = key.strip().strip('" ,')
                value = value.strip().strip('" ,')

                if key in keys:
                    if key == "geoinfo":
                        if "geoinfo" not in data:
                            data["geoinfo"] = {}
                        sub_key_value = value.split(':', 1)
                        if len(sub_key_value) == 2:
                            sub_key, sub_value = sub_key_value
                            sub_key = sub_key.strip().strip('" ,')
                            sub_value = sub_value.strip().strip('" ,')
                            if sub_key in geoinfo_keys:
                                data["geoinfo"][sub_key] = sub_value
                    elif key == "tasktype":
                        if key not in data:
                            data[key] = []
                        data[key].append(value.strip())
                    elif key == "bereich":
                        if current_dict is not None:
                            current_dict[key] = {"bereichDate": value.strip()}
                    else:
                        data[key] = value.strip()
                        current_dict = data

    return data

def parse_generated_text(generated_text):
    # Define a pattern to match a JSON-like object with specific keys
    pattern = r'\{\s*"title"\s*:\s*"[^"]*"\s*,\s*"description"\s*:\s*"[^"]*"\s*,\s*"startdate"\s*:\s*"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"\s*,\s*"enddate"\s*:\s*"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"\s*,\s*"geoinfo"\s*:\s*\{\s*"name"\s*:\s*"[^"]*"\s*,\s*"latitude"\s*:\s*"\d*"\s*,\s*"longitude"\s*:\s*"\d*"\s*\}\s*,\s*"duration"\s*:\s*"\d+(\.\d+)?"\s*,\s*"purpose"\s*:\s*"[^"]*"\s*,\s*"role"\s*:\s*"[^"]*"\s*,\s*"rank"\s*:\s*"[^"]*"\s*,\s*"phase"\s*:\s*"[^"]*"\s*,\s*"unit"\s*:\s*"[^"]*"\s*,\s*"level"\s*:\s*"[^"]*"\s*,\s*"tasktype"\s*:\s*\[\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*""\s*\]\s*,\s*"bereich"\s*:\s*"[^"]*"\s*\}'
    
    match = re.search(pattern, generated_text, re.DOTALL)
    print("Match:",match)
    if match:
        generated_json_str = match.group(0)
        return generated_json_str
    else:
        return None

# Function to generate JSON objects based on a structured prompt
def generate_activity_data():
    prompt = """Generate me a JSON object with the following properties:
    "title": {
        "type": "string",
        "description": "Title of the training event"
    },
    "description": {
        "type": "string",
        "description": "Description of the training event"
    },
    "startdate": {
        "type": "string",
        "format": "date-time",
        "description": "Start date and time of the training event in ISO 8601 format"
    },
    "enddate": {
        "type": "string",
        "format": "date-time",
        "description": "End date and time of the training event in ISO 8601 format"
    },
    "geoinfo": {
        "type": "object",
        "description": "Geographical information about the location",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the location"
            },
            "latitude": {
                "type": "string",
                "description": "Latitude coordinate of the location"
            },
            "longitude": {
                "type": "string",
                "description": "Longitude coordinate of the location"
            }
        },
    },
    "duration": {
        "type": "string",
        "description": "Duration of the training event in hours (e.g., '1.5' for 1.5 hours)"
    },
    "purpose": {
        "type": "string",
        "description": "Purpose of the training event"
    },
    "role": {
        "type": "string",
        "description": "Role in the training event"
    },
    "rank": {
        "type": "string",
        "description": "Rank associated with the training event"
    },
    "phase": {
        "type": "string",
        "description": "Phase of the training event"
    },
    "unit": {
        "type": "string",
        "description": "Unit involved in the training event"
    },
    "level": {
        "type": "string",
        "description": "Level of the training event"
    },
    "tasktype": {
        "type": "array",
        "items": {
            "type": "string"
        },
        "description": "Types of tasks associated with the training event"
    },
    "bereich": {
        "type": "string",
        "description": "Area or field related to the training event"
    }
    }
    """

    output = generator(prompt, max_new_tokens=700, num_return_sequences=1, do_sample=True)[0]
    generated_text = output['generated_text']
    print("Generated Text:",generated_text)

    # Construct the JSON object from tokens
    generated_json = extract_key_value_pairs(generated_text)
    return generated_json

# Generate JSON objects
for i in range(1):
    generated_activities = generate_activity_data()

    # Output the generated data
    if generated_activities:
        print(json.dumps(generated_activities, indent=2, ensure_ascii=False))
    else:
        print("Failed to generate valid JSON object matching the schema.")
