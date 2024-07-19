import datetime
import random
import time
from faker import Faker
import numpy as np

# Initialize Faker
fake = Faker(['de_AT', 'de_DE'])

def handle_goals(data=None, attributes=None, num_records=None, action='generate'):
    if action not in ['generate', 'anonymize']:
        raise ValueError("action must be either 'generate' or 'anonymize'")
    
    # Flatten nested list if action is 'anonymize'
    if action == 'anonymize':
        if isinstance(data, list) and isinstance(data[0], list):
            data = data[0]  # Get the actual data from the first element of the outer list
        if not isinstance(data, list) or not all(isinstance(record, dict) for record in data):
            raise TypeError("Data should be a list of dictionaries")
    
    results_times = []

    # Define larger lists for 'type' and 'level' with German/Austrian context
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
        data = []
    
    for _ in range(num_records or len(data)):
        record = {}
        if action == 'anonymize':
            record = data[_]
        start_time = time.time()

        for attribute in attributes:
            if attribute == 'type':
                record[attribute] = random.choice(types)
            elif attribute == 'level':
                record[attribute] = random.choice(levels)
            elif attribute == 'description':
                start_date = datetime.date(1970, 1, 1)
                end_date = datetime.date(2023, 12, 31)
                record[attribute] = str(fake.date_between(start_date=start_date, end_date=end_date))
            else:
                record[attribute] = fake.word()
        
        end_time = time.time()
        results_times.append(end_time - start_time)
        
        if action == 'generate':
            data.append(record)
    
    return data, results_times
