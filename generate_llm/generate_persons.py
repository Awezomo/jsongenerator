import json
import json
import re
import time
import torch
from transformers import GPTNeoForCausalLM, GPT2Tokenizer, set_seed, pipeline

def generate_persons(selected_attributes, uploadedData, num_records=1):
    model_name = "gpt_neo_finetuned"  
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPTNeoForCausalLM.from_pretrained(model_name)

    # Set the device to GPU if available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    # Set the generator pipeline
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=device)

    # Function to generate JSON objects in batches
    def generate_person_data_batch(prompts):
        generated_persons = []
        result_times = []

        for prompt in prompts:
            while True:
                output = generator(prompt, max_new_tokens=200, num_return_sequences=1, do_sample=True)[0]
                if isinstance(output, dict):
                    generated_text = output['generated_text']

                    # Extract JSON part from the generated text using regex
                    pattern = r'\{\s*"userName":\s*"[^"]+",\s*"password":\s*"[^"]+",\s*"email":\s*"[^"]+",\s*"firstName":\s*"([^"]+)",\s*"lastName":\s*"([^"]+)",\s*"birthDate":\s*"[^"]+"\s*\}'
                    match = re.search(pattern, generated_text, re.DOTALL)
                    if match:
                        extracted_json = match.group(0)
                        try:
                            person_data = json.loads(extracted_json)
                            
                            # Validate firstName and lastName
                            if not person_data['firstName'].istitle() or any(char.isdigit() for char in person_data['firstName']):
                                print(f"Invalid firstName: {person_data['firstName']}")
                                break  # Break the inner loop to regenerate the prompt and retry
                            
                            if not person_data['lastName'].istitle() or any(char.isdigit() for char in person_data['lastName']):
                                print(f"Invalid lastName: {person_data['lastName']}")
                                break  # Break the inner loop to regenerate the prompt and retry
                            
                            generated_persons.append(person_data)
                            result_times.append(time.time())
                            break  # Break the inner loop to move to the next prompt
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON: {extracted_json}")
                    else:
                        print(f"Invalid JSON format, regenerating prompt...")
                        break  # Break the inner loop to regenerate the prompt and retry
                else:
                    print(f"Unexpected output type: {type(output)}")
                    break  # Break the inner loop to regenerate the prompt and retry
        
        assert len(generated_persons) == len(result_times), "Mismatch between generated persons and result times"
        return generated_persons, result_times

    # Define prompts for JSON object generation
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
    """ for _ in range(num_records)  # Adjust the range based on how many JSON objects you want to generate
    ]

    # Generate JSON objects in batches
    generated_persons = generate_person_data_batch(prompts)

    return generated_persons