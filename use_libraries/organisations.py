import datetime
import random
import time
from faker import Faker
import numpy as np

# Initialize Faker
fake = Faker(['de_AT', 'de_DE'])

def handle_organisations(data=None, attributes=None, num_records=None, action='generate'):
    if action not in ['generate', 'anonymize']:
        raise ValueError("action must be either 'generate' or 'anonymize'")
    
    # Flatten nested list if action is 'anonymize'
    if action == 'anonymize':
        if isinstance(data, list) and isinstance(data[0], list):
            data = data[0]  # Get the actual data from the first element of the outer list
        if not isinstance(data, list) or not all(isinstance(record, dict) for record in data):
            raise TypeError("Data should be a list of dictionaries")
    
    results_times = []

    if action == 'generate':
        data = []
    
    organisations = {'Rotes Kreuz': 'RK', 'Caritas': 'C', 'Diakonie': 'D', 'Volkshilfe': 'VH', 'Arbeiter Samariter Bund': 'ASB', 'Malteser': 'M', 'Johanniter': 'J', 'Pfarrcaritas': 'PC', 'Feuerwehr': 'FF', 'Polizei': 'P'}
    
    for _ in range(num_records or len(data)):
        record = {}
        if action == 'anonymize':
            record = data[_]
        start_time = time.time()

        for attribute in attributes:
            if attribute == 'organisationName':
                org_name = random.choice(list(organisations.keys()))
                record[attribute] = org_name
            elif attribute == 'abbreviation':
                org_name = record.get('organisationName')
                record[attribute] = organisations.get(org_name, '')
            elif attribute == 'orgDescription':
                record[attribute] = fake.text()
            elif attribute == 'orgWebsite':
                record[attribute] = fake.url()
            elif attribute == 'orgImage':
                record[attribute] = fake.image_url()
            elif attribute == 'orgTags':
                record[attribute] = ', '.join(fake.words(nb=3))
            elif attribute == 'orgLocation':
                record[attribute] = fake.city()
            else:
                record[attribute] = fake.word()
        
        end_time = time.time()
        results_times.append(end_time - start_time)
        
        if action == 'generate':
            data.append(record)
    
    return data, results_times