import json
import json
import re
import torch
from transformers import GPTNeoForCausalLM, GPT2Tokenizer, set_seed, pipeline

def generate_badges(num_records=1):
    model_name = "gpt_neo_badges_finetuned"  
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPTNeoForCausalLM.from_pretrained(model_name)

    # Set the device to GPU if available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    # Set the generator pipeline
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=device)

    # Function to generate JSON objects in batches
    def generate_badge_data(prompts):
        generated_badges = []

        for prompt in prompts:
            while True:
                output = generator(prompt, max_new_tokens=200, num_return_sequences=1, do_sample=True)[0]
                if isinstance(output, dict):
                    generated_text = output['generated_text']

                    # Extract JSON part from the generated text using regex
                    pattern = r'\{\s*"badgeName":\s*"[^"]+",\s*"badgeDescription":\s*"[^"]+",\s*"badgeIssuedOn":\s*"\d{4}-\d{2}-\d{2}"\s*\}'
                    match = re.search(pattern, generated_text, re.DOTALL)
                    if match:
                        extracted_json = match.group(0)
                        try:
                            badge_data = json.loads(extracted_json)
                            
                            #if any(char.isdigit() for char in badge_data['badgeName']):
                            #    print(f"Invalid badgeName: {badge_data['badgeName']}")
                            #    break

                            #if any(char.isdigit() for char in badge_data['badgeDescription']):
                            #    print(f"Invalid lastName: {badge_data['badgeDescription']}")
                            #    break 
                            
                            generated_badges.append(badge_data)
                            break  # Break the inner loop to move to the next prompt
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON: {extracted_json}")
                    else:
                        print(f"Invalid JSON format, regenerating prompt...")
                        break  # Break the inner loop to regenerate the prompt and retry
                else:
                    print(f"Unexpected output type: {type(output)}")
                    break  # Break the inner loop to regenerate the prompt and retry

        return generated_badges

    # Define prompts for JSON object generation
    prompts = [
        f"""Generate a JSON object with the following properties:
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

    Here is a reference:
    [
        {
            "badgeName": "THL Gold",
            "badgeDescription": "THL Gold Abzeichen",
            "badgeIssuedOn": "1989-10-29"
        }
    ]
    Mix the results up.
    JSON object:
    """ for _ in range(num_records)  # Adjust the range based on how many JSON objects you want to generate
    ]

    # Generate JSON objects in batches
    return generate_badge_data(prompts)