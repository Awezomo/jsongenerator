import torch
from transformers import GPT2Tokenizer, GPTNeoForCausalLM, pipeline
import re
from datasets import Dataset
import time

def initialize_model_and_pipeline(model_name):
    """
    Initialize and return the tokenizer, model, and pipeline.

    Args:
        model_name (str): The model name.

    Returns:
        tuple: (tokenizer, model, generator pipeline)
    """
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPTNeoForCausalLM.from_pretrained(model_name)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=0 if device == "cuda" else -1)
    return tokenizer, model, generator

def extract_keys_from_text(text, keys):
    """
    Extract specified keys and their values from the generated text.

    Args:
        text (str): Generated text containing JSON-like structure.
        keys (list): List of keys to extract values for.

    Returns:
        dict: Extracted key-value pairs.
    """
    patterns = {
        'title': r'"title"\s*:\s*"([^"]*)"',
        'description': r'"description"\s*:\s*"([^"]*)"',
        'startdate': r'"startdate"\s*:\s*"([^"]*)"',
        'enddate': r'"enddate"\s*:\s*"([^"]*)"',
        'geoinfo.name': r'"geoinfo"\s*:\s*\{\s*"name"\s*:\s*"([^"]*)"',
        'geoinfo.latitude': r'"geoinfo"\s*:\s*\{\s*"latitude"\s*:\s*"([^"]*)"',
        'geoinfo.longitude': r'"geoinfo"\s*:\s*\{\s*"longitude"\s*:\s*"([^"]*)"',
        'duration': r'"duration"\s*:\s*"([^"]*)"',
        'purpose': r'"purpose"\s*:\s*"([^"]*)"',
        'role': r'"role"\s*:\s*"([^"]*)"',
        'rank': r'"rank"\s*:\s*"([^"]*)"',
        'phase': r'"phase"\s*:\s*"([^"]*)"',
        'unit': r'"unit"\s*:\s*"([^"]*)"',
        'level': r'"level"\s*:\s*"([^"]*)"',
        'tasktype': r'"tasktype"\s*:\s*\[([^\]]*)\]',
        'bereich': r'"bereich"\s*:\s*"([^"]*)"'
    }

    text = text.replace('\n', ' ').replace('\r', '').replace('“', '"').replace('”', '"')
    features = {}
    
    for key in keys:
        pattern = patterns.get(key)
        if pattern:
            match = re.search(pattern, text)
            if match:
                value = match.group(1)
                if key == 'tasktype':
                    features[key] = [item.strip().strip('"') for item in value.split(',')]
                else:
                    features[key] = value

    return features

def anonymize_activities(data, selected_attributes):
    """
    Anonymize activity records using a GPT-Neo model.

    Args:
        data (list): List of activity records to anonymize.
        selected_attributes (list): List of attributes to anonymize.

    Returns:
        list: Anonymized activity records.
    """
    model_name = "gpt_neo_activities_finetuned"
    tokenizer, model, generator = initialize_model_and_pipeline(model_name)

    anonymized_data = []
    prompts = [
        f"""Generate new values for the following attributes: {', '.join(f'"{attr}"' for attr in selected_attributes)}
        JSON object:""" for _ in data
    ]

    dataset = Dataset.from_dict({"prompts": prompts})
    batch_size = 1

    while len(anonymized_data) < len(data):
        for i in range(0, len(prompts), batch_size):
            batch_prompts = dataset["prompts"][i:i + batch_size]
            start_time = time.time()
            batch_outputs = generator(batch_prompts, max_length=2048, num_return_sequences=1, do_sample=True)
            result_times = [time.time() - start_time]

            generated_texts = [output[0]['generated_text'] for output in batch_outputs]
            for idx, generated_text in enumerate(generated_texts):
                new_values = extract_keys_from_text(generated_text, selected_attributes)

                anonymized_record = {}
                for attr in selected_attributes:
                    old_value = data[i + idx].get(attr, "")
                    new_value = new_values.get(attr, "")
                    anonymized_record[attr] = new_value if new_value and new_value != old_value else ""

                anonymized_data.append({**data[i + idx], **anonymized_record})

                if len(anonymized_data) >= len(data):
                    break

    return anonymized_data

def generate_activities(num_records):
    """
    Generate activity records using a GPT-Neo model.

    Args:
        num_records (int): Number of activity records to generate.

    Returns:
        tuple: A tuple containing:
            - List of generated activities.
            - List of times taken for each generation.
            - List indicating validity of each generated activity.
    """
    model_name = "gpt_neo_activities_finetuned"
    tokenizer, model, generator = initialize_model_and_pipeline(model_name)

    default_activity = {
        'title': '', 'description': '', 'startdate': '', 'enddate': '', 
        'geoinfo': {'name': '', 'latitude': '', 'longitude': ''},
        'duration': '', 'purpose': '', 'role': '', 'rank': '', 'phase': '', 
        'unit': '', 'level': '', 'tasktype': [], 'bereich': ''
    }

    prompts = [
        f"""Generate a JSON object with the following properties:
        "title": {{ "type": "string", "describes": "Title of the training event" }},
        "description": {{ "type": "string", "describes": "Description of the training event" }},
        "startdate": {{ "type": "string", "format": "date-time", "describes": "Start date and time in ISO 8601 format" }},
        "enddate": {{ "type": "string", "format": "date-time", "describes": "End date and time in ISO 8601 format" }},
        "geoinfo": {{ "type": "object", "describes": "Geographical information", "properties": {{ "name": {{ "type": "string", "describes": "Name of the location" }}, "latitude": {{ "type": "string", "describes": "Latitude coordinate" }}, "longitude": {{ "type": "string", "describes": "Longitude coordinate" }} }} }},
        "duration": {{ "type": "string", "describes": "Duration in hours (e.g., '1.5')" }},
        "purpose": {{ "type": "string", "describes": "Purpose of the training event" }},
        "role": {{ "type": "string", "describes": "Role in the training event" }},
        "rank": {{ "type": "string", "describes": "Rank associated with the training event" }},
        "phase": {{ "type": "string", "describes": "Phase of the training event" }},
        "unit": {{ "type": "string", "describes": "Unit involved in the training event" }},
        "level": {{ "type": "string", "describes": "Level of the training event" }},
        "tasktype": {{ "type": "array", "items": {{ "type": "string" }}, "describes": "Types of tasks" }},
        "bereich": {{ "type": "string", "describes": "Area or field related to the training event" }}
        JSON object:
        """ for _ in range(num_records)
    ]

    dataset = Dataset.from_dict({"prompts": prompts})
    generated_activities = []
    result_times = []
    valid_result = []
    batch_size = 1

    while len(generated_activities) < num_records:
        for i in range(0, len(prompts), batch_size):
            batch_prompts = dataset["prompts"][i:i + batch_size]
            start_time = time.time()
            batch_outputs = generator(batch_prompts, max_length=2048, num_return_sequences=1, do_sample=True)
            result_times.append(time.time() - start_time)

            generated_texts = [output[0]['generated_text'] for output in batch_outputs]
            for generated_text in generated_texts:
                features = extract_keys_from_text(generated_text, default_activity.keys())
                if is_valid_result(features, default_activity):
                    generated_activities.append(features)
                    valid_result.append(True)
                    if len(generated_activities) >= num_records:
                        break
                else:
                    valid_result.append(False)

            if len(generated_activities) >= num_records:
                break

    return generated_activities[:num_records], result_times, valid_result

def is_valid_result(data, schema):
    """
    Check if the generated data contains more than half of the schema keys with valid values.

    Args:
        data (dict): Generated data to validate.
        schema (dict): Schema to validate against.

    Returns:
        bool: True if valid, False otherwise.
    """
    total_keys = len(schema)
    valid_key_count = sum(
        1 for key in schema 
        if ('.' in key and 
            key.split('.')[0] in data and 
            key.split('.')[1] in data[key.split('.')[0]] and 
            data[key.split('.')[0]][key.split('.')[1]] not in ("", [], {}, None)) or
           (key not in data or data[key] not in ("", [], {}, None)) == False
    )
    return valid_key_count > (total_keys / 2)
