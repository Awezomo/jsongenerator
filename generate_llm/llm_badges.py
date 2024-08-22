import json
import re
import torch
import time  # Import the time module to track the time taken for generating results
from transformers import GPTNeoForCausalLM, GPT2Tokenizer, pipeline

def generate_badges(num_records=1):
    model_name = "gpt_neo_badges_finetuned"  
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPTNeoForCausalLM.from_pretrained(model_name)

    # Set the device to GPU if available; otherwise, use CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    # Initialize the text generation pipeline with the model and tokenizer
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=device)

    # Lists to store the times taken for generation and validity of results
    result_times = []
    valid_result = []

    # Function to generate JSON badge data based on provided prompts
    def generate_badge_data(prompts):
        generated_badges = []

        for prompt in prompts:
            while True:
                start_time = time.time()  # Start timing the generation process
                
                # Generate text from the model based on the prompt
                output = generator(prompt, max_new_tokens=200, num_return_sequences=1, do_sample=True)[0]
                result_times.append(time.time() - start_time)  # Record the elapsed time

                if isinstance(output, dict):
                    generated_text = output['generated_text']

                    # Define a regex pattern to extract JSON from the generated text
                    pattern = r'\{\s*"badgeName":\s*"[^"]+",\s*"badgeDescription":\s*"[^"]+",\s*"badgeIssuedOn":\s*"\d{4}-\d{2}-\d{2}"\s*\}'
                    match = re.search(pattern, generated_text, re.DOTALL)
                    if match:
                        extracted_json = match.group(0)
                        try:
                            # Load the extracted JSON into a Python dictionary
                            badge_data = json.loads(extracted_json)
                            generated_badges.append(badge_data)
                            valid_result.append(True)  # Mark the result as valid
                            break  # Exit the loop to process the next prompt
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON: {extracted_json}")
                            valid_result.append(False)  # Mark the result as invalid
                            continue
                    else:
                        print(f"Invalid JSON format, regenerating prompt...")
                        valid_result.append(False)  # Mark the result as invalid
                        continue  
                else:
                    print(f"Unexpected output type: {type(output)}")
                    valid_result.append(False)  # Mark the result as invalid
                    continue

        return generated_badges

    # Define prompts for generating JSON badge objects
    prompts = [
        f"""
        I want you to generate a JSON object for volunteering badges.
        Generate a JSON object with the following properties:
        "badgeName": {{
            "type": "string",
            "description": "The name of the badge"
        }},
        "badgeDescription": {{
            "type": "string",
            "description": "The description of a badge"
        }},
        "badgeIssuedOn": {{
            "type": "string",
            "description": "The date of the badge being issued"
        }}
     
        JSON object:
        """ for _ in range(num_records)  # Create multiple prompts based on the number of records required
    ]

    # Generate badges using the prompts
    generated_badges = generate_badge_data(prompts)

    # Output the timing and validity results along with the generated badges
    print(result_times)
    print("Generated badges:", generated_badges)
    print("Validity of results:", valid_result)

    return generated_badges, result_times, valid_result

def anonymize_badges(data, attributes_to_anonymize):
    model_name = "gpt_neo_badges_finetuned"  
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPTNeoForCausalLM.from_pretrained(model_name)

    # Set the device to GPU if available; otherwise, use CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    # Initialize the text generation pipeline with the model and tokenizer
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=device)

    # Function to generate new values for specific attributes
    def generate_new_value(attribute):
        prompt = f"""
        Generate a new value for the attribute "{attribute}" of a JSON object representing a volunteering badge.
        The structure should be like:
        "{attribute}": "..."
        """
        # Generate text for the new attribute value
        output = generator(prompt, max_new_tokens=30, num_return_sequences=1, do_sample=True)[0]
        generated_text = output['generated_text']

        # Extract the new value from the generated text
        pattern = rf'"{attribute}":\s*"([^"]+)"'
        match = re.search(pattern, generated_text)
        if match:
            return match.group(1)
        return None

    # Anonymize specified attributes in the provided badge data
    for badge in data:
        for attribute in attributes_to_anonymize:
            if attribute in badge:
                new_value = generate_new_value(attribute)
                if new_value:
                    badge[attribute] = new_value

    return data
