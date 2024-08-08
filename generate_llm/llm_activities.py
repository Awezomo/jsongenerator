import torch
from transformers import GPT2Tokenizer, GPTNeoForCausalLM, pipeline
import re
from datasets import Dataset
import time

def generate_activities(num_records):
    model_name = "gpt_neo_activities_finetuned"  # Update to the appropriate model name
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPTNeoForCausalLM.from_pretrained(model_name)

    # Set the device to GPU if available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    # Set the generator pipeline
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=0 if device == "cuda" else -1)

    # Define the default schema
    default_activity = {
        'title': '',
        'description': '',
        'startdate': '',
        'enddate': '',
        'geoinfo': {
            'name': '',
            'latitude': '',
            'longitude': ''
        },
        'duration': '',
        'purpose': '',
        'role': '',
        'rank': '',
        'phase': '',
        'unit': '',
        'level': '',
        'tasktype': [],
        'bereich': ''
    }

    def extract_keys_from_text(text):
        # Define patterns for key extraction
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

        features = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                value = match.group(1)
                if key == 'tasktype':
                    features[key] = [item.strip().strip('"') for item in value.split(',')]
                else:
                    features[key] = value

        return features

    def process_text(text):
        # Clean up text
        text = text.replace('\n', ' ').replace('\r', '').replace('“', '"').replace('”', '"')
        
        # Extract keys and their values
        features = extract_keys_from_text(text)
        
        # Ensure all keys are present and fill with default values if missing
        processed_object = {}
        for key in default_activity:
            if '.' in key:
                main_key, sub_key = key.split('.')
                if main_key not in processed_object:
                    processed_object[main_key] = {}
                processed_object[main_key][sub_key] = features.get(key, default_activity[main_key][sub_key])
            else:
                processed_object[key] = features.get(key, default_activity[key])

        return processed_object

    def is_valid_result(data, schema):
        total_keys = len(schema)
        valid_key_count = 0
        
        # Check if more than half of the schema's keys are present and non-empty
        for key in schema:
            if '.' in key:
                main_key, sub_key = key.split('.')
                if main_key in data and sub_key in data[main_key] and data[main_key][sub_key] not in ("", [], {}, None):
                    valid_key_count += 1
            else:
                if key in data and data[key] not in ("", [], {}, None):
                    valid_key_count += 1
        
        return valid_key_count > (total_keys / 2)

    prompts = [
        f"""Generate a JSON object with the following properties:
        "title": {{
            "type": "string",
            "descripes": "Title of the training event"
        }},
        "description": {{
            "type": "string",
            "describes": "Description of the training event"
        }},
        "startdate": {{
            "type": "string",
            "format": "date-time",
            "describes": "Start date and time of the training event in ISO 8601 format"
        }},
        "enddate": {{
            "type": "string",
            "format": "date-time",
            "describes": "End date and time of the training event in ISO 8601 format"
        }},
        "geoinfo": {{
            "type": "object",
            "describes": "Geographical information about the location",
            "properties": {{
                "name": {{
                    "type": "string",
                    "describes": "Name of the location"
                }},
                "latitude": {{
                    "type": "string",
                    "describes": "Latitude coordinate of the location"
                }},
                "longitude": {{
                    "type": "string",
                    "describes": "Longitude coordinate of the location"
                }}
            }}
        }},
        "duration": {{
            "type": "string",
            "describes": "Duration of the training event in hours (e.g., '1.5' for 1.5 hours)"
        }},
        "purpose": {{
            "type": "string",
            "describes": "Purpose of the training event"
        }},
        "role": {{
            "type": "string",
            "describes": "Role in the training event"
        }},
        "rank": {{
            "type": "string",
            "describes": "Rank associated with the training event"
        }},
        "phase": {{
            "type": "string",
            "describes": "Phase of the training event"
        }},
        "unit": {{
            "type": "string",
            "describes": "Unit involved in the training event"
        }},
        "level": {{
            "type": "string",
            "describes": "Level of the training event"
        }},
        "tasktype": {{
            "type": "array",
            "items": {{
                "type": "string"
            }},
            "describes": "Types of tasks associated with the training event"
        }},
        "bereich": {{
            "type": "string",
            "describes": "Area or field related to the training event"
        }}
        JSON object:
        """ for _ in range(num_records)
    ]

    dataset = Dataset.from_dict({"prompts": prompts})
    
    generated_activities = []
    batch_size = 1  
    
    result_times = []
    valid_result = []

    while len(generated_activities) < num_records:
        for i in range(0, len(prompts), batch_size):
            batch_prompts = dataset["prompts"][i:i+batch_size]
            start_time = time.time()
            batch_outputs = generator(batch_prompts, max_length=2048, num_return_sequences=1, do_sample=True)
            end_time = time.time()
            result_times.append(end_time - start_time)
            
            generated_texts = [output[0]['generated_text'] for output in batch_outputs]
            extracted_data = [process_text(text) for text in generated_texts]
            
            for data in extracted_data:
                if is_valid_result(data, default_activity):
                    generated_activities.append(data)
                    valid_result.append(True)
                    if len(generated_activities) >= num_records:
                        break
                else:
                    valid_result.append(False)
                    
            if len(generated_activities) >= num_records:
                break

    print(f"Result times: {result_times}")
    print(f"Generated activities: {generated_activities}")
    print(f"Valid results: {valid_result}")
    return generated_activities[:num_records], result_times, valid_result
