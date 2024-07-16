import json
import json
import re
import time
import torch
from transformers import GPTNeoForCausalLM, GPT2Tokenizer, pipeline
from datasets import Dataset

result_times = []
valid_result = []

def generate_data(jsonType, uploadedData, num_records):

    if jsonType == 'persons':
        return generate_persons(uploadedData, num_records)
    elif jsonType == 'badges':
        return generate_badges(uploadedData, num_records)
    elif jsonType == 'activities':
        return generate_activities(uploadedData, num_records)
    elif jsonType == 'organisations':
        return generate_organisations(uploadedData, num_records)
    elif jsonType == 'goals':
        return generate_goals(uploadedData, num_records)
    else:
        return []
    
def generate_persons(prompts, num_records):
    model_name = "gpt_neo_finetuned"
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPTNeoForCausalLM.from_pretrained(model_name)

    # Set the device to GPU if available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    # Set the generator pipeline
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=device)

    def extract_json_objects(generated_texts):
        pattern = r'\{\s*"userName":\s*"[^"]+",\s*"password":\s*"[^"]+",\s*"email":\s*"[^"]+",\s*"firstName":\s*"([^"]+)",\s*"lastName":\s*"([^"]+)",\s*"birthDate":\s*"[^"]+"\s*\}'
        extracted_data = []
        
        for text in generated_texts:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                extracted_json = match.group(0)
                try:
                    person_data = json.loads(extracted_json)
                    # Correct firstName and lastName to title case
                    person_data['firstName'] = person_data['firstName'].title()
                    person_data['lastName'] = person_data['lastName'].title()
                    
                    # Validate firstName and lastName for digits
                    if not any(char.isdigit() for char in person_data['firstName']) and \
                       not any(char.isdigit() for char in person_data['lastName']):
                        extracted_data.append(person_data)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON: {extracted_json}")
            else:
                print(f"Invalid JSON format: {text}")
        
        return extracted_data

    prompts = [
        f"""Generate a JSON object with the following properties:
        "userName": {{
            "type": "string",
            "description": "The username of the person, for a volunteering platform"
        }},
        "password": {{
            "type": "string",
            "description": "a password one person would choose"
        }},
        "email": {{
            "type": "string",
            "description": "the mail address of the person, most of the users are from Austria, so use reasonable domains. Make sure the address is not usually using another name than the first and last names generated"
        }},
        "firstName": {{
            "type": "string",
            "description": "the first name of the person. most of the users are from Austria, so use reasonable names"
        }},
        "lastName": {{
            "type": "string",
            "description": "the last name of the person. most of the users are from Austria, so use reasonable names"
        }},
        "birthDate": {{
            "type": "string",
            "description": "the birth date of the person"
        }}
        JSON object:
        """ for _ in range(num_records)
    ]

    dataset = Dataset.from_dict({"prompts": prompts})
    
    generated_persons = []
    batch_size = 1  
    
    result_times.clear()
    valid_result.clear()
    while len(generated_persons) < num_records:
        for i in range(0, len(prompts), batch_size):
            batch_prompts = dataset["prompts"][i:i+batch_size]
            batch_outputs = generator(batch_prompts, max_new_tokens=200, num_return_sequences=1, do_sample=True)
            generated_texts = [output[0]['generated_text'] for output in batch_outputs]
            extracted_data = extract_json_objects(generated_texts)
            generated_persons.extend(extracted_data)
            result_times.append(time.time())
            if extracted_data != []:
                valid_result.append(True)
            else:
                valid_result.append(False)
           
            if len(generated_persons) >= num_records:
                break
    print(result_times)
    print("Gen pers",generated_persons)
    print("Valid result",valid_result)
    return generated_persons[:num_records], result_times, valid_result


def generate_badges(selected_attributes, uploadedData, num_records):
           pass
def generate_activities(selected_attributes, uploadedData, num_records):
           pass
def generate_organisations(selected_attributes, uploadedData, num_records):
            pass

def generate_goals(selected_attributes, uploadedData, num_records):
           pass