import json
import re
import torch
import time
from transformers import GPT2Tokenizer, GPTNeoForCausalLM, pipeline

def generate_organisations(num_records=1):
    """
    Generate a list of organizations as JSON objects using a GPT-Neo model.

    Args:
        num_records (int): Number of organizations to generate.

    Returns:
        tuple: (list of generated organizations, list of result times, list of validity flags)
    """
    model_name = "gpt_neo_orgs_finetuned"  
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPTNeoForCausalLM.from_pretrained(model_name)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=0 if device == "cuda" else -1)

    result_times = []
    valid_result = []

    def generate_org_data(prompts):
        """
        Generate organization data from prompts.

        Args:
            prompts (list of str): List of prompts to generate organizations.

        Returns:
            list of dict: Generated organizations.
        """
        generated_orgs = []

        for prompt in prompts:
            while True:
                start_time = time.time()
                output = generator(prompt, max_new_tokens=200, num_return_sequences=1, do_sample=True)[0]
                result_times.append(time.time() - start_time)
                
                if isinstance(output, dict):
                    generated_text = output['generated_text']
                    pattern = r'\{\s*"organisationName":\s*"[^"]+",\s*"abbreviation":\s*"[^"]+",\s*"orgDescription":\s*"[^"]+",\s*"orgWebsite":\s*"https://[^"]+",\s*"orgImage":\s*"https://[^"]+",\s*"orgTags":\s*"([^"]+)(,\s*[^"]+)*",\s*"orgLocation":\s*"[^"]+"\s*\}'
                    match = re.search(pattern, generated_text, re.DOTALL)
                    
                    if match:
                        try:
                            org_data = json.loads(match.group(0))
                            generated_orgs.append(org_data)
                            valid_result.append(True)
                            break
                        except json.JSONDecodeError:
                            valid_result.append(False)
                    else:
                        valid_result.append(False)
                else:
                    valid_result.append(False)

        return generated_orgs

    # Define prompts for JSON object generation
    prompts = [
        f"""Generate a JSON object for a volunteering organization with:
        "organisationName": (string) Name of the organization,
        "abbreviation": (string) Abbreviated name,
        "orgDescription": (string) Description of the organization,
        "orgWebsite": (string) Website URL,
        "orgImage": (string) Image/Logo URL,
        "orgTags": (string) Tags describing activities,
        "orgLocation": (string) Location.
        JSON object:""" for _ in range(num_records)
    ]

    # Generate JSON objects in batches
    generated_orgs = generate_org_data(prompts)

    # Print or return results
    print("Result times:", result_times)
    print("Generated organizations:", generated_orgs)
    print("Validity of results:", valid_result)

    return generated_orgs, result_times, valid_result

def anonymize_organisations(data, attributes_to_anonymize):
    """
    Anonymize specified attributes in the organization data.

    Args:
        data (list of dict): List of organization records to anonymize.
        attributes_to_anonymize (list of str): List of attributes to anonymize.

    Returns:
        list of dict: Anonymized organization data.
    """
    model_name = "gpt_neo_orgs_finetuned"  
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPTNeoForCausalLM.from_pretrained(model_name)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=0 if device == "cuda" else -1)

    def generate_new_value(attribute):
        """
        Generate a new value for a specific attribute.

        Args:
            attribute (str): Attribute to generate a new value for.

        Returns:
            str: New value for the attribute.
        """
        prompt = f"""Generate a new value for the attribute "{attribute}" of a JSON object representing a volunteering organization:
        "{attribute}": "..."
        """
        output = generator(prompt, max_new_tokens=20, num_return_sequences=1, do_sample=True)[0]
        generated_text = output['generated_text']
        pattern = rf'"{attribute}":\s*"([^"]+)"'
        match = re.search(pattern, generated_text)
        return match.group(1) if match else None

    # Anonymize the selected attributes in the provided data
    for org in data:
        for attribute in attributes_to_anonymize:
            if attribute in org:
                new_value = generate_new_value(attribute)
                if new_value:
                    org[attribute] = new_value

    return data
