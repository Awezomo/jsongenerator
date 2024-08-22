import json
import re
import torch
import time
from transformers import GPT2Tokenizer, GPTNeoForCausalLM, pipeline

def generate_goals(num_records=1):
    """
    Generate a list of goals as JSON objects using a GPT-Neo model.

    Args:
        num_records (int): Number of goals to generate.

    Returns:
        tuple: (list of generated goals, list of result times, list of validity flags)
    """
    model_name = "gpt_neo_goals_finetuned"  
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPTNeoForCausalLM.from_pretrained(model_name)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=0 if device == "cuda" else -1)

    result_times = []
    valid_result = []

    def generate_goals_data(prompts):
        """
        Generate goals data from prompts.

        Args:
            prompts (list of str): List of prompts to generate goals.

        Returns:
            list of dict: Generated goals.
        """
        generated_goals = []
        
        for prompt in prompts:
            while True:
                start_time = time.time()
                output = generator(prompt, max_new_tokens=200, num_return_sequences=1, do_sample=True)[0]
                result_times.append(time.time() - start_time)
                
                if isinstance(output, dict):
                    generated_text = output['generated_text']
                    pattern = r'\{\s*"type":\s*"[^"]+",\s*"level":\s*"[^"]+",\s*"description":\s*"[^"]+"\s*\}'
                    match = re.search(pattern, generated_text, re.DOTALL)
                    
                    if match:
                        try:
                            goal_data = json.loads(match.group(0))
                            if all(not any(char.isdigit() for char in goal_data[field]) for field in ['type', 'level', 'description']):
                                generated_goals.append(goal_data)
                                valid_result.append(True)
                                break
                            else:
                                valid_result.append(False)
                        except json.JSONDecodeError:
                            valid_result.append(False)
                    else:
                        valid_result.append(False)
                else:
                    valid_result.append(False)

        return generated_goals

    prompts = [
        f"""Generate a JSON object for a volunteering goal with:
        "type": (string) The type of the goal,
        "level": (string) The level of the goal,
        "description": (string) A description of the goal.
        JSON object:""" for _ in range(num_records)
    ]
    
    generated_goals = generate_goals_data(prompts)
    print("Result times:", result_times)
    print("Generated goals:", generated_goals)
    print("Validity of results:", valid_result)

    return generated_goals, result_times, valid_result

def anonymize_goals(data, attributes_to_anonymize):
    """
    Anonymize specified attributes in the goals data.

    Args:
        data (list of dict): List of goal records to anonymize.
        attributes_to_anonymize (list of str): List of attributes to anonymize.

    Returns:
        list of dict: Anonymized goals data.
    """
    model_name = "gpt_neo_goals_finetuned"  
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
        prompt = f"""Generate a new value for the attribute "{attribute}" of a JSON object representing a volunteering goal:
        "{attribute}": "..."
        """
        output = generator(prompt, max_new_tokens=20, num_return_sequences=1, do_sample=True)[0]
        generated_text = output['generated_text']
        pattern = rf'"{attribute}":\s*"([^"]+)"'
        match = re.search(pattern, generated_text)
        return match.group(1) if match else None

    for goal in data:
        for attribute in attributes_to_anonymize:
            if attribute in goal:
                new_value = generate_new_value(attribute)
                if new_value:
                    goal[attribute] = new_value

    return data
