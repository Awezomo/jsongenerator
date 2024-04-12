import json
from faker import Faker

fake = Faker()

def generate_synthetic_data(json_data):
    # Parse JSON data
    try:
        data = json.loads(json_data)
    except json.JSONDecodeError:
        return {'error': 'Invalid JSON format'}

    # Generate synthetic data based on JSON schema
    synthetic_data = {}
    #test
    # Example: Generate synthetic data based on JSON schema
    # Replace this logic with your own data generation logic
    for key, value in data.items():
        if isinstance(value, str):
            synthetic_data[key] = fake.text(max_nb_chars=100)
        elif isinstance(value, int):
            synthetic_data[key] = fake.random_int()
        elif isinstance(value, float):
            synthetic_data[key] = fake.random_number()
        else:
            synthetic_data[key] = fake.word()

    return synthetic_data
