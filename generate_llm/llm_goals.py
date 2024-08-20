import json
import re
import torch
import time  # Import the time module to track result times
from transformers import GPTNeoForCausalLM, GPT2Tokenizer, set_seed, pipeline

def generate_goals(num_records=1):
    model_name = "gpt_neo_goals_finetuned"  
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
    def generate_goals_data(prompts):
        generated_goals = []

        for prompt in prompts:
            while True:
                start_time = time.time()  # Record the start time
                
                output = generator(prompt, max_new_tokens=200, num_return_sequences=1, do_sample=True)[0]
                
                result_times.append(time.time() - start_time)  # Calculate and store the elapsed time

                if isinstance(output, dict):
                    generated_text = output['generated_text']

                    # Extract JSON part from the generated text using regex
                    pattern = r'\{\s*"type":\s*"[^"]+",\s*"level":\s*"[^"]+",\s*"description":\s*"[^"]+"\s*\}'
                    match = re.search(pattern, generated_text, re.DOTALL)
                    if match:
                        extracted_json = match.group(0)
                        try:
                            goal_data = json.loads(extracted_json)
                            
                            # Validate fields to ensure no digits are present
                            if any(char.isdigit() for char in goal_data['type']):
                                print(f"Invalid type: {goal_data['type']}")
                                valid_result.append(False)  # Mark as an invalid result
                                continue

                            if any(char.isdigit() for char in goal_data['level']):
                                print(f"Invalid level: {goal_data['level']}")
                                valid_result.append(False)  # Mark as an invalid result
                                continue

                            if any(char.isdigit() for char in goal_data['description']):
                                print(f"Invalid description: {goal_data['description']}")
                                valid_result.append(False)  # Mark as an invalid result
                                continue

                            generated_goals.append(goal_data)
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

        return generated_goals

    # Define prompts for JSON object generation
    prompts = [
        f"""
        I want to have a JSON object of a volunteering goal.
        Generate a JSON object with the following properties:
    "type": {{
        "type": "string",
        "describes": "The type of the volunteering goal"
    }},
    "level": {{
        "type": "string",
        "describes": "The level of the volunteering goal"
    }},
    "description": {{
        "type": "string",
        "describes": "The description of the volunteering goal, usually consisting of type and level."
    }}

    JSON object:
    """ for _ in range(num_records)  # Adjust the range based on how many JSON objects you want to generate
    ]

    # Generate JSON objects in batches
    generated_goals = generate_goals_data(prompts)

    # Print or return the timing and validity results along with the generated data
    print(result_times)
    print("Generated goals:", generated_goals)
    print("Validity of results:", valid_result)

    return generated_goals, result_times, valid_result
