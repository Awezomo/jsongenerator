import json
import re
import time
import torch
from transformers import GPT2Tokenizer, GPTNeoForCausalLM, pipeline
from datasets import Dataset

result_times = []
valid_result = []

def anonymize_persons(data, selected_attributes):
    """
    Anonymize specified attributes in the provided person data.

    Args:
        data (list of dict): List of person records to anonymize.
        selected_attributes (list of str): List of attributes to anonymize.

    Returns:
        list of dict: Anonymized person data.
    """
    model_name = "gpt_neo_finetuned"
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPTNeoForCausalLM.from_pretrained(model_name)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=0 if device == "cuda" else -1)

    def extract_values_from_text(generated_text, attributes):
        """Extract values for specified attributes from the generated text."""
        extracted_data = {}
        for attr in attributes:
            pattern = re.compile(rf'"{attr}"\s*:\s*"([^"]*)"')
            match = pattern.search(generated_text)
            extracted_data[attr] = match.group(1) if match else ""
        return extracted_data

    prompts = [
        f"""Generate new values for these attributes: {", ".join(selected_attributes)}.
        Ensure the output is a valid JSON object with only these attributes.
        JSON object:""" for _ in range(len(data))
    ]

    dataset = Dataset.from_dict({"prompts": prompts})
    anonymized_persons = []
    batch_size = 1
    
    result_times.clear()
    valid_result.clear()

    while len(anonymized_persons) < len(data):
        for i in range(0, len(prompts), batch_size):
            batch_prompts = dataset["prompts"][i:i + batch_size]
            batch_outputs = generator(batch_prompts, max_new_tokens=150, num_return_sequences=1, do_sample=True)
            generated_texts = [output['generated_text'] for output in batch_outputs]

            for idx, generated_text in enumerate(generated_texts):
                extracted_data = extract_values_from_text(generated_text, selected_attributes)
                anonymized_record = {}
                original_record = data[i + idx]

                for attr in selected_attributes:
                    old_value = original_record.get(attr, "")
                    new_value = extracted_data.get(attr, "")
                    anonymized_record[attr] = new_value if new_value and new_value != old_value else ""

                anonymized_persons.append({**original_record, **anonymized_record})

            if len(anonymized_persons) >= len(data):
                break

    return anonymized_persons[:len(data)]

def generate_persons(num_records):
    """
    Generate a list of person records as JSON objects using a GPT-Neo model.

    Args:
        num_records (int): Number of person records to generate.

    Returns:
        tuple: (list of generated persons, list of result times, list of validity flags)
    """
    model_name = "gpt_neo_finetuned"
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPTNeoForCausalLM.from_pretrained(model_name)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=0 if device == "cuda" else -1)

    def extract_json_objects(generated_texts):
        """Extract valid JSON objects from generated texts."""
        pattern = r'\{\s*"userName":\s*"[^"]+",\s*"password":\s*"[^"]+",\s*"email":\s*"[^"]+",\s*"firstName":\s*"([^"]+)",\s*"lastName":\s*"([^"]+)",\s*"birthDate":\s*"[^"]+"\s*\}'
        extracted_data = []

        for text in generated_texts:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    person_data = json.loads(match.group(0))
                    person_data['firstName'] = person_data['firstName'].title()
                    person_data['lastName'] = person_data['lastName'].title()
                    
                    if not any(char.isdigit() for char in person_data['firstName']) and \
                       not any(char.isdigit() for char in person_data['lastName']):
                        extracted_data.append(person_data)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON: {match.group(0)}")
            else:
                print(f"Invalid JSON format: {text}")

        return extracted_data

    prompts = [
        f"""Generate a JSON object with:
        "userName": (string) Username for a volunteering platform,
        "password": (string) Password a person might choose,
        "email": (string) Email address, preferably from an Austrian domain,
        "firstName": (string) First name, reasonable for Austrian names,
        "lastName": (string) Last name, reasonable for Austrian names,
        "birthDate": (string) Birth date.
        JSON object:""" for _ in range(num_records)
    ]

    dataset = Dataset.from_dict({"prompts": prompts})
    generated_persons = []
    batch_size = 1

    result_times.clear()
    valid_result.clear()

    while len(generated_persons) < num_records:
        for i in range(0, len(prompts), batch_size):
            batch_prompts = dataset["prompts"][i:i + batch_size]
            batch_outputs = generator(batch_prompts, max_new_tokens=256, num_return_sequences=1, do_sample=True)
            generated_texts = [output[0]['generated_text'] for output in batch_outputs]
            extracted_data = extract_json_objects(generated_texts)
            generated_persons.extend(extracted_data)
            result_times.append(time.time())
            valid_result.append(True if extracted_data else False)

            if len(generated_persons) >= num_records:
                break

    print("Result times:", result_times)
    print("Generated persons:", generated_persons)
    print("Validity of results:", valid_result)

    return generated_persons[:num_records], result_times, valid_result
