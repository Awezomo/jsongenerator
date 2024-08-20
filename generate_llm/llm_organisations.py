import json
import re
import torch
import time  # Import the time module to track result times
from transformers import GPTNeoForCausalLM, GPT2Tokenizer, set_seed, pipeline

def generate_organisations(num_records=1):
    model_name = "gpt_neo_orgs_finetuned"  
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPTNeoForCausalLM.from_pretrained(model_name)

    # Set the device to GPU if available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    # Set the generator pipeline
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=device)

    # Initialize lists to store result times and validity
    result_times = []
    valid_result = []

    # Function to generate JSON objects in batches
    def generate_org_data(prompts):
        generated_orgs = []

        for prompt in prompts:
            while True:
                start_time = time.time()  # Record the start time
                
                output = generator(prompt, max_new_tokens=200, num_return_sequences=1, do_sample=True)[0]
                
                result_times.append(time.time() - start_time)  # Calculate and store the elapsed time

                if isinstance(output, dict):
                    generated_text = output['generated_text']

                    # Extract JSON part from the generated text using regex
                    pattern = r'\{\s*"organisationName":\s*"[^"]+",\s*"abbreviation":\s*"[^"]+",\s*"orgDescription":\s*"[^"]+",\s*"orgWebsite":\s*"https://[^"]+",\s*"orgImage":\s*"https://[^"]+",\s*"orgTags":\s*"([^"]+)(,\s*[^"]+)*",\s*"orgLocation":\s*"[^"]+"\s*\}'
                    match = re.search(pattern, generated_text, re.DOTALL)
                    if match:
                        extracted_json = match.group(0)
                        try:
                            org_data = json.loads(extracted_json)
                            generated_orgs.append(org_data)
                            valid_result.append(True)  # Mark as a valid result
                            break  # Break the inner loop to move to the next prompt
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON: {extracted_json}")
                            valid_result.append(False)  # Mark as an invalid result
                            continue
                    else:
                        print(f"Invalid JSON format, regenerating prompt...")
                        valid_result.append(False)  # Mark as an invalid result
                        continue
                else:
                    print(f"Unexpected output type: {type(output)}")
                    valid_result.append(False)  # Mark as an invalid result
                    continue

        return generated_orgs

    # Define prompts for JSON object generation
    prompts = [
        f"""
        I want to have a JSON object of a volunteering organisation.
        Generate a JSON object with the following properties:
    "organisationName": {{
        "type": "string",
        "describes": "Name of the volunteering organisation"
    }},
    "abbreviation": {{
        "type": "string",
        "describes": "Abbreviated name of the volunteering organisation"
    }},
    "orgDescription": {{
        "type": "string",
        "describes": "The description of the volunteering organisation."
    }},
    "orgWebsite": {{
        "type": "string",
        "describes": "The website of the volunteering organisation."
    }},
    "orgImage": {{
        "type": "string",
        "describes": "The image/logo of the volunteering organisation."
    }},
    "orgTags": {{
        "type": "string",
        "describes": "The tags of the volunteering organisation that describe its activities."
    }},
    "orgLocation": {{
        "type": "string",
        "describes": "The location of the volunteering organisation."
    }}

    JSON object:
    """ for _ in range(num_records)  # Adjust the range based on how many JSON objects you want to generate
    ]

    # Generate JSON objects in batches
    generated_orgs = generate_org_data(prompts)

    # Print or return the timing and validity results along with the generated data
    print(result_times)
    print("Generated organisations:", generated_orgs)
    print("Validity of results:", valid_result)

    return generated_orgs, result_times, valid_result
