import datetime
import random
import time
from faker import Faker
import numpy as np

# Initialize Faker with German locales
fake = Faker(['de_AT', 'de_DE'])

def handle_goals(data=None, attributes=None, num_records=None, action='generate'):
    """
    Generate or anonymize goal data based on the provided action and attributes.

    Args:
        data (list, optional): Existing data to be anonymized. Should be a list of dictionaries.
        attributes (list): List of attributes to be included in the data.
        num_records (int, optional): Number of records to generate if action is 'generate'.
        action (str): Action to perform, either 'generate' for creating new data or 'anonymize' for modifying existing data.

    Returns:
        tuple: A tuple containing the processed data and the time taken for each record.
    """

    # Validate the action parameter
    if action not in ['generate', 'anonymize']:
        raise ValueError("action must be either 'generate' or 'anonymize'")
    
    # Process the data if the action is 'anonymize'
    if action == 'anonymize':
        if isinstance(data, list) and isinstance(data[0], list):
            data = data[0]  # Flatten the nested list if necessary
        if not isinstance(data, list) or not all(isinstance(record, dict) for record in data):
            raise TypeError("Data should be a list of dictionaries")
    
    results_times = []  # List to store the time taken to process each record

    # Define possible values for 'type' and 'level'
    types = [
        'Gemeinschaftsdienst', 'Fundraising', 'Bildung', 'Umweltschutz', 
        'Gesundheit', 'Tierschutz', 'Kultur', 'Katastrophenhilfe', 
        'Wohlfahrtspflege', 'Mentoring', 'Notfallhilfe', 'Jugendprogramme'
    ]
    
    levels = [
        'Anfänger', 'Fortgeschritten', 'Experte', 'Profi', 
        'Neuling', 'Erfahren', 'Fachkraft', 'Leiter'
    ]
    
    if action == 'generate':
        data = []  # Initialize an empty list if generating new data
    
    # Generate or anonymize records based on the provided attributes
    for _ in range(num_records or len(data)):
        record = {}
        if action == 'anonymize':
            record = data[_]  # Use existing data for anonymization
        start_time = time.time()  # Start timing the record processing

        for attribute in attributes:
            if attribute == 'type':
                record[attribute] = random.choice(types)  # Randomly select a type
            elif attribute == 'level':
                record[attribute] = random.choice(levels)  # Randomly select a level
            elif attribute == 'description':
                # Create a description based on the type and level
                record[attribute] = f"Errungenschaft in {record['type']} der Stufe {record['level']}"
            else:
                record[attribute] = fake.word()  # Generate a fake word for other attributes
        
        end_time = time.time()  # End timing the record processing
        results_times.append(end_time - start_time)  # Record the time taken

        if action == 'generate':
            data.append(record)  # Append the new record to the data list
    
    return data, results_times  # Return the processed data and the times taken
